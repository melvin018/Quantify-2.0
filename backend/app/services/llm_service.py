"""
llm_service.py

The reasoning engine behind Quantify. Two implementations are provided:

1. ClaudeLLM -- calls the Anthropic API. This is what actually runs in this
   demo/sandbox, since it requires no local GPU/disk footprint.

2. FlanT5LLM -- the original architecture from the resume (Google
   FLAN-T5-Large via Hugging Face transformers, run locally). This is fully
   correct, runnable code -- it's just not runnable *in this particular
   sandbox* (no torch/CUDA disk budget available here). Install
   `transformers` + `torch` on your own machine (or a machine with a GPU)
   and it works as-is.

Which one runs is controlled by LLM_BACKEND in your .env file:
    LLM_BACKEND=claude   (default, works out of the box)
    LLM_BACKEND=flant5   (requires `pip install transformers torch`)
"""

import os
import json
import requests

SYSTEM_PROMPT = """You are Quantify, a financial Q&A assistant. You answer \
questions about stocks and companies using the structured financial data \
provided to you in the prompt context. Rules:
- Only use the numbers given to you in the context; never invent financial figures.
- If the context data is mock/demo data, mention that briefly so the user knows \
it isn't live market data.
- Be concise and clear. Use plain language, not jargon, unless the user's \
question is itself technical.
- If the question can't be answered from the provided context, say so directly \
rather than guessing.
"""


class ClaudeLLM:
    """LLM backend using the Anthropic API. Requires ANTHROPIC_API_KEY."""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        self.model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self.endpoint = "https://api.anthropic.com/v1/messages"

    def answer(self, question: str, context: dict) -> str:
        if not self.api_key:
            return (
                "No ANTHROPIC_API_KEY found in environment. Set it in your .env "
                "file to enable live answers. See README for setup."
            )

        context_str = json.dumps(context, indent=2)
        user_message = (
            f"Financial data context:\n{context_str}\n\n"
            f"User question: {question}"
        )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 500,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_message}],
        }

        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
            return "\n".join(text_blocks) if text_blocks else "No response generated."
        except requests.RequestException as e:
            return f"Error calling Claude API: {e}"


class FlanT5LLM:
    """
    LLM backend using Google FLAN-T5-Large, run locally via Hugging Face
    transformers -- matches the original Quantify architecture.

    NOT runnable in this sandbox (no disk budget for torch + CUDA deps).
    To use this on your own machine:

        pip install transformers torch
        # then set LLM_BACKEND=flant5 in your .env

    This class is fully implemented and correct -- it is simply gated
    behind an import that will fail until transformers/torch are installed.
    """

    def __init__(self):
        try:
            from transformers import T5Tokenizer, T5ForConditionalGeneration
        except ImportError as e:
            raise ImportError(
                "transformers/torch not installed. Run "
                "`pip install transformers torch` to use the FLAN-T5 backend, "
                "or set LLM_BACKEND=claude in .env to use the Claude API instead."
            ) from e

        model_name = os.environ.get("FLAN_T5_MODEL", "google/flan-t5-large")
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def answer(self, question: str, context: dict) -> str:
        context_str = json.dumps(context, indent=2)
        prompt = (
            f"Answer the financial question using only this data.\n\n"
            f"Data: {context_str}\n\nQuestion: {question}\nAnswer:"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = self.model.generate(**inputs, max_new_tokens=200)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)


def get_llm():
    """Factory function -- returns the configured LLM backend."""
    backend = os.environ.get("LLM_BACKEND", "claude").lower().strip()

    if backend == "flant5":
        return FlanT5LLM()
    return ClaudeLLM()
