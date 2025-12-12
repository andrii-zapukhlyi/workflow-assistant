FROM python:3.10-slim AS builder
WORKDIR /app

RUN apt-get update && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && rm -rf /root/.cache/pip /root/.cache/pypoetry

COPY . /app

FROM python:3.10-slim
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=builder /app /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]