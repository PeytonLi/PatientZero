FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PATIENT_ZERO_ROOT=/app \
    PATIENT_ZERO_HOST=0.0.0.0

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY artifacts ./artifacts
COPY data/graph ./data/graph
COPY scripts ./scripts

RUN pip install --no-cache-dir .

EXPOSE 8080
CMD ["python", "scripts/demo.py"]
