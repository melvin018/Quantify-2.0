"""
database.py

Stores chat history (question, answer, symbols referenced, timestamp) for
the Quantify chatbot.

Matches the original architecture's use of MySQL. Since this sandbox has
no MySQL server running, this module connects to MySQL if MYSQL_HOST is
set in .env, and otherwise falls back to a local SQLite file
(quantify_demo.db) so the app still has working persistence in a demo
environment without requiring a database server to be stood up first.

The schema is intentionally simple and works identically on both backends
since it avoids MySQL-specific syntax.
"""

import os
import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    symbols TEXT,
    intent TEXT,
    created_at TEXT NOT NULL
);
"""

# MySQL-compatible version of the same schema, for reference / use with a
# real MySQL server (AUTOINCREMENT -> AUTO_INCREMENT, TEXT sizes, etc.)
MYSQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    symbols VARCHAR(255),
    intent VARCHAR(50),
    created_at DATETIME NOT NULL
);
"""

_SQLITE_PATH = os.path.join(os.path.dirname(__file__), "..", "quantify_demo.db")


def _use_mysql() -> bool:
    return bool(os.environ.get("MYSQL_HOST", "").strip())


def get_connection():
    if _use_mysql():
        try:
            import mysql.connector
        except ImportError as e:
            raise ImportError(
                "MYSQL_HOST is set but mysql-connector-python isn't installed. "
                "Run `pip install mysql-connector-python`."
            ) from e

        return mysql.connector.connect(
            host=os.environ["MYSQL_HOST"],
            port=int(os.environ.get("MYSQL_PORT", 3306)),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=os.environ.get("MYSQL_DATABASE", "quantify"),
        )

    return sqlite3.connect(_SQLITE_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(MYSQL_SCHEMA if _use_mysql() else SCHEMA)
    conn.commit()
    conn.close()


def log_interaction(question: str, answer: str, symbols: list, intent: str):
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if _use_mysql() else "?"
    query = (
        f"INSERT INTO chat_history (question, answer, symbols, intent, created_at) "
        f"VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})"
    )
    cursor.execute(query, (
        question,
        answer,
        ",".join(symbols),
        intent,
        datetime.now(timezone.utc).isoformat(),
    ))
    conn.commit()
    conn.close()


def get_recent_history(limit: int = 20) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = "%s" if _use_mysql() else "?"
    cursor.execute(
        f"SELECT question, answer, symbols, intent, created_at "
        f"FROM chat_history ORDER BY id DESC LIMIT {placeholder}",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "question": r[0], "answer": r[1], "symbols": r[2],
            "intent": r[3], "created_at": r[4],
        }
        for r in rows
    ]
