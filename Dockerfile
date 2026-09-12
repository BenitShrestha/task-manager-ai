FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY . .

RUN pip install uv && uv sync --frozen --no-dev

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT"]