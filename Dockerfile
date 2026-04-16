FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-root

COPY . .

WORKDIR /app/src

CMD python -m alembic upgrade head && uvicorn tvde_qr.main:app --host 0.0.0.0 --port $PORT