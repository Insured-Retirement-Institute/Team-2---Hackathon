"""Tests for Responsible AI admin API. Mocks DB so no Postgres is required.

Run from repo root:  PYTHONPATH=api/src python -m pytest api/tests/test_responsible_ai.py -v
Or with api installed:  cd api && pip install -e . && pytest tests/test_responsible_ai.py -v
"""
import sys
from pathlib import Path

# Ensure the api package from api/src is used (not the project-level api folder)
_api_src = Path(__file__).resolve().parent.parent / "src"
if _api_src.exists() and str(_api_src) not in sys.path:
    sys.path.insert(0, str(_api_src))
# Clear cached api (app) package so we load from api/src; keep api.tests*
for key in list(sys.modules.keys()):
    if key == "api" or (key.startswith("api.") and not key.startswith("api.tests")):
        sys.modules.pop(key, None)

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers import responsible_ai


@pytest.fixture
def client():
    """Minimal app with only the responsible_ai router; fetch_rows is patched per test."""
    app = FastAPI()
    app.include_router(responsible_ai.router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_responsible_ai_stats_returns_shape(client):
    """GET /admin/responsible-ai/stats returns the expected keys (mocked empty)."""
    with patch("api.routers.responsible_ai.fetch_rows", new_callable=AsyncMock) as m:
        m.return_value = [{
            "total_runs": 0,
            "success_count": 0,
            "agent_one_runs": 0,
            "agent_two_runs": 0,
            "agent_three_runs": 0,
            "agent_two_with_explanation": 0,
            "guardrail_triggered_count": 0,
        }]
        resp = client.get("/admin/responsible-ai/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "from_date" in data
    assert "to_date" in data
    assert data["total_runs"] == 0
    assert data["success_rate"] == 0.0
    assert data["explainability_coverage_pct"] == 0.0


@pytest.mark.asyncio
async def test_responsible_ai_stats_with_rows(client):
    """GET /admin/responsible-ai/stats computes success_rate and explainability from rows."""
    with patch("api.routers.responsible_ai.fetch_rows", new_callable=AsyncMock) as m:
        m.return_value = [{
            "total_runs": 10,
            "success_count": 8,
            "agent_one_runs": 3,
            "agent_two_runs": 5,
            "agent_three_runs": 2,
            "agent_two_with_explanation": 4,
            "guardrail_triggered_count": 0,
        }]
        resp = client.get("/admin/responsible-ai/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_runs"] == 10
    assert data["success_count"] == 8
    assert data["success_rate"] == 80.0
    assert data["agent_two_with_explanation"] == 4
    assert data["explainability_coverage_pct"] == 80.0  # 4/5


@pytest.mark.asyncio
async def test_responsible_ai_events_list(client):
    """GET /admin/responsible-ai/events returns { events: [] }."""
    with patch("api.routers.responsible_ai.fetch_rows", new_callable=AsyncMock) as m:
        m.return_value = []
        resp = client.get("/admin/responsible-ai/events?limit=10&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data
    assert data["events"] == []


@pytest.mark.asyncio
async def test_responsible_ai_event_by_id_404(client):
    """GET /admin/responsible-ai/events/{id} returns 404 when not found."""
    with patch("api.routers.responsible_ai.fetch_rows", new_callable=AsyncMock) as m:
        m.return_value = []
        resp = client.get("/admin/responsible-ai/events/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
