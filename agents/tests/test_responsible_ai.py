"""Tests for Responsible AI schemas and audit writer. No DB required."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest

from agents.responsible_ai_schemas import AgentId, AgentRunEvent
from agents.audit_writer import persist_event, persist_agent_two_payload


def test_agent_run_event_build_and_serialize():
    """AgentRunEvent can be built and serialized for persistence."""
    event = AgentRunEvent(
        event_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        agent_id=AgentId.agent_two,
        run_id=str(uuid.uuid4()),
        client_id_scope="Marty McFly",
        input_summary={"sections_present": ["suitability", "clientProfile"]},
        success=True,
        explanation_summary="Recommendations generated from suitability and profile.",
        data_sources_used=["sureify_products", "db_suitability"],
        choice_criteria=["risk_tolerance", "time_horizon"],
        input_validation_passed=True,
        guardrail_triggered=None,
        payload_ref=None,
    )
    assert event.agent_id == AgentId.agent_two
    assert event.success is True
    # Model can be serialized to dict for DB/API
    d = event.model_dump()
    assert d["agent_id"] == "agent_two"
    assert "event_id" in d and "timestamp" in d


def test_persist_event_without_db_returns_false():
    """Without DATABASE_URL, persist_event returns False and does not raise."""
    # Ensure no DB env so we don't accidentally hit a real DB
    old_url = os.environ.pop("DATABASE_URL", None)
    old_host = os.environ.pop("RDSHOST", None)
    try:
        event = AgentRunEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=AgentId.agent_one,
            run_id=None,
            client_id_scope="test",
            input_summary={},
            success=True,
        )
        result = persist_event(event)
        assert result is False
    finally:
        if old_url is not None:
            os.environ["DATABASE_URL"] = old_url
        if old_host is not None:
            os.environ["RDSHOST"] = old_host


def test_persist_agent_two_payload_without_db_returns_none():
    """Without DATABASE_URL, persist_agent_two_payload returns None and does not raise."""
    old_url = os.environ.pop("DATABASE_URL", None)
    old_host = os.environ.pop("RDSHOST", None)
    try:
        result = persist_agent_two_payload(
            run_id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            client_id="Marty McFly",
            payload={"explanation": {"summary": "test"}, "recommendations": []},
        )
        assert result is None
    finally:
        if old_url is not None:
            os.environ["DATABASE_URL"] = old_url
        if old_host is not None:
            os.environ["RDSHOST"] = old_host


def test_agent_id_values():
    """AgentId enum has expected values for DB constraint."""
    assert AgentId.agent_one.value == "agent_one"
    assert AgentId.agent_two.value == "agent_two"
    assert AgentId.agent_three.value == "agent_three"
