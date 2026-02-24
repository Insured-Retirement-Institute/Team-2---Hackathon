FROM symetra.jfrog.io/bddbrn-docker-virtual/python:3.13-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy files needed for build
COPY pyproject.toml uv.lock ./
COPY src/ src/

# Create venv and install dependencies
RUN uv venv /.venv
ENV PATH="/.venv/bin:$PATH"
RUN uv pip install .

# Build wheels
RUN mkdir -p /wheels && uv build -o /wheels

FROM symetra.jfrog.io/bddbrn-docker-virtual/python:3.13-slim-trixie AS app

WORKDIR /app

# Copy uv to have pip alternative, or ensure pip is available
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels

# Install wheels using uv pip (more reliable than system pip)
RUN /bin/uv pip install --system /wheels/*.whl

# Copy queries directory
COPY queries/ /app/queries/

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE $PORT
ARG build_version="test"
ENV BUILD_VERSION=$build_version

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
