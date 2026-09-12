FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY . .

RUN pip install uv && uv sync --frozen --no-dev

CMD ["sh", "-c", "uv run streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]