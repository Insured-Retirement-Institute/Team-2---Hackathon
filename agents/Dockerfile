FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy workspace config files first (for layer caching)
COPY pyproject.toml uv.lock ./
COPY api/pyproject.toml api/
COPY agents/pyproject.toml agents/
COPY schemas/pyproject.toml schemas/

# Copy source code
COPY api/src/ api/src/
COPY agents/src/ agents/src/
COPY schemas/src/ schemas/src/

# Install dependencies using uv sync
RUN uv sync --frozen --no-dev --package agents

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE $PORT
ARG build_version="test"
ENV BUILD_VERSION=$build_version

CMD ["uv", "run", "uvicorn", "agents.server:app", "--host", "0.0.0.0", "--port", "8000"]
