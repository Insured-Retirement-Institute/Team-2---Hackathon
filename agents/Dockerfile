FROM python:3.13-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy workspace files needed for dependency resolution
COPY uv.lock pyproject.toml ./
COPY agents/pyproject.toml agents/
COPY api/pyproject.toml api/

# Copy source code
COPY agents/ agents/
COPY api/src/ api/src/

# Create venv and install dependencies (not packages themselves)
RUN uv venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Install dependencies from pyproject.toml without editable mode
RUN uv pip install \
    "strands-agents>=0.1" \
    "pydantic>=2.0" \
    "python-dotenv>=1.0" \
    "psycopg2-binary>=2.9" \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.32.0" \
    "httpx>=0.28.0" \
    "asyncpg>=0.31.0" \
    "pyjwt[crypto]>=2.11.0"

FROM python:3.13-slim-trixie AS app

WORKDIR /app

# Copy uv for pip alternative
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy venv from builder
COPY --from=builder /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Copy source code directly (keeps agents/ and api/ structure)
COPY agents/ /app/agents/
COPY api/src/api/ /app/api/

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE $PORT

ARG build_version="test"
ENV BUILD_VERSION=$build_version

CMD ["uvicorn", "agents.server:app", "--host", "0.0.0.0", "--port", "8000"]
