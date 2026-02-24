# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-enabled solution for managing in-force annuities - part of the Insured Retirement Institute Hackathon. The project provides a unified dashboard with automated processing, compliance documentation, and opportunity identification for annuity management.

## Build & Run Commands

### Setup
```bash
# Install dependencies (requires uv package manager)
uv sync

# Copy environment template
cp .env.example .env
```

### Running Locally

**API Server:**
```bash
cd api && uv run uvicorn api.main:app --reload
# http://localhost:8000
```

**Agents (tool-only mode, no LLM):**
```bash
SUREIFY_AGENT_TOOL_ONLY=1 PYTHONPATH=. python -m agents.main
```

**Agents (with Bedrock LLM):**
```bash
PYTHONPATH=. python -m agents.main
```

**Docker Compose:**
```bash
docker-compose -f docker-compose.dev.yml up  # Development
docker-compose up                              # Production-like
```

### Testing
```bash
pytest                    # All tests
pytest --cov              # With coverage
```

### Task Runner (mise)
```bash
mise run generate-models       # Generate Pydantic from sureify.json OpenAPI spec
mise run pgschema:plan         # Preview database schema changes
mise run pgschema:apply        # Apply schema changes
mise run ecr:build-push        # Build and push Docker image to ECR
mise run eks:deploy            # Deploy to EKS (CNPG + DB + App)
```

## Architecture

### Monorepo Structure
- **api/** - FastAPI service integrating with Sureify CoreCONECT Edge API
- **agents/** - Strands-based AI agent for book-of-business analysis
- **database/** - PostgreSQL schema definitions (managed by pgschema)
- **k8s/** - Kubernetes/EKS deployment configs

### API Package (`api/src/api/`)
- `main.py` - FastAPI app entry point
- `sureify_client.py` - OAuth2 authenticated HTTP client for Sureify
- `sureify_models.py` - Generated Pydantic models from Sureify OpenAPI
- `database.py` - PostgreSQL async connection pool
- `routers/passthrough.py` - Sureify API proxy endpoints
- `routers/policies.py` - Database-backed policy endpoints

### Agents Package (`agents/`)
- `main.py` - Strands agent definition with Bedrock integration
- `sureify_client.py` - Sureify client (mock or real)
- `logic.py` - Business rules (replacements, data quality, income activation)
- `schemas.py` - Output shapes (PolicyOutput, BookOfBusinessOutput)
- `iri_api_spec.yaml` - **OpenAPI 3.0.3 source of truth for IRI API**
- `iri_schemas.py` - Generated Pydantic models from IRI spec

**Agent Output Modes:**
- `SUREIFY_AGENT_TOOL_ONLY=1` - Mock data, no LLM
- `SUREIFY_AGENT_IRI_ONLY=1` - IRI alerts format output
- `SUREIFY_AGENT_SCHEMA_ONLY=1` - Book-of-business JSON schema

### Database (`database/tables/`)
Tables: `clients`, `products`, `contract_summary`, `riders`, `client_suitability_profiles`, `index_options`

Schema management: Design in SQL files, preview with `pgschema:plan`, apply with `pgschema:apply`

### Deployment
- **EKS Auto Mode** with CloudNativePG (CNPG) for PostgreSQL
- Config in `k8s/eksctl-cluster.yaml` and `k8s/dev-cluster.yaml`

## Key Patterns

1. **OpenAPI as Source of Truth**: `iri_api_spec.yaml` drives DB design and Pydantic models. Regenerate after spec changes:
   ```bash
   PYTHONPATH=. python -m agents.regenerate_iri_schemas
   ```

2. **Dual Output Formats**: Book-of-business (snake_case) and IRI alerts (camelCase) from same data

3. **Async-First**: All I/O uses async (FastAPI, asyncpg, httpx)

4. **Mock-Friendly**: Agents work with mock Sureify data when API credentials not provided

## Configuration

- `mise.toml` - Task definitions
- `mise.local.toml` - Local credentials (git-ignored)
- `.env.example` - Environment template (AWS, RDS, Sureify, IRI)
