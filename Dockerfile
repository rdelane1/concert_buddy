FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --locked --no-dev

EXPOSE 8080

CMD ["sh", "-c", "uv run uvicorn src.concert_buddy.server:app --host 0.0.0.0 --port ${PORT:-8080}"]