# Running integration tests

## Recommended (Python 3.13 + uv)

From the repo root, with [uv](https://docs.astral.sh/uv/) and Python 3.13:

```bash
# All tests (agents + API)
uv run pytest agents/tests api/tests -v

# Agents tests only (requires strands-agents)
uv run pytest agents/tests -v

# API tests only (requires api deps)
uv run pytest api/tests -v
```

The root `pyproject.toml` sets `pythonpath = [".", "api/src"]` so both `agents` and `api` are importable. Use `PYTHONPATH=api/src` only when running API tests if the wrong `api` package is loaded (e.g. `PYTHONPATH=api/src uv run pytest api/tests -v`).

## Without strands (partial agents tests)

These tests do **not** require the `strands` package or a database:

- `agents/tests/test_responsible_ai.py` – Responsible AI schemas and audit writer
- `agents/tests/test_agent_two_integration.py` – Profile row mapping, e-apply payload, upsert (no DB)

On Python 3.9 you may need:

```bash
pip install pytest pydantic psycopg2-binary eval_type_backport
PYTHONPATH=. pytest agents/tests/test_responsible_ai.py agents/tests/test_agent_two_integration.py -v
```

Tests that import agent one/two/three `main` modules will be skipped or fail without `strands-agents` installed.

## Summary

| Test path | Needs | Notes |
|-----------|--------|--------|
| `agents/tests/test_responsible_ai.py` | pydantic, psycopg2 | No DB; persist_* returns False/None |
| `agents/tests/test_agent_two_integration.py` | pydantic, audit_writer | Profile/e-apply; one test skips without strands |
| `agents/tests/test_agents_work.py` | strands-agents | Agent one/two/three tools and run_chat |
| `api/tests/test_responsible_ai.py` | fastapi, api (api/src) | Mocks DB |
| `api/tests/test_health.py` | - | Placeholder |
