# Quantify backend -- FastAPI service
FROM python:3.12-slim

WORKDIR /app

# Use the Docker-specific requirements file, which includes
# mysql-connector-python since docker-compose.yml runs a MySQL container
# alongside this service. If you're not using Docker, see
# backend/requirements.txt instead (SQLite by default, no MySQL needed).
COPY docker/requirements-docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
