FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv
COPY . .
RUN uv sync --frozen
CMD ["sh", "-c", "uv run streamlit run app.py --server.port $PORT --server.address 0.0.0.0"]