"""Tests that agents run as expected (no LLM/DB required for agent_one/agent_two)."""
from __future__ import annotations

import json
import os
from unittest.mock import patch, MagicMock

import pytest

# Agent one: schema-only and tool-only paths (no Strands LLM)
def test_agent_one_schema_only():
    """Agent one with SUREIFY_AGENT_SCHEMA_ONLY prints JSON schema and emits event."""
    from agents.agent_one.main import get_book_of_business_json_schema, _emit_agent_one_event

    schema_str = get_book_of_business_json_schema()
    assert isinstance(schema_str, str)
    schema = json.loads(schema_str)
    assert "$defs" in schema or "properties" in schema
    assert "PolicyNotification" in schema_str or "policy" in schema_str.lower()


def test_agent_one_tool_only_produces_book_of_business():
    """Agent one tool get_book_of_business_with_notifications_and_flags returns valid JSON."""
    from agents.agent_one.main import get_book_of_business_with_notifications_and_flags

    out = get_book_of_business_with_notifications_and_flags("Marty McFly")
    data = json.loads(out)
    assert "customer_identifier" in data
    assert "policies" in data
    assert isinstance(data["policies"], list)


def test_agent_one_main_schema_only_path():
    """Agent one main() with SUREIFY_AGENT_SCHEMA_ONLY runs and emits event (no crash)."""
    from agents.agent_one import main

    with patch.dict(os.environ, {"SUREIFY_AGENT_SCHEMA_ONLY": "1"}, clear=False):
        with patch("agents.agent_one.main.persist_event", return_value=False):
            main()
    # No exception = path works


def test_agent_one_main_tool_only_path():
    """Agent one main() with SUREIFY_AGENT_TOOL_ONLY runs and emits event (no crash)."""
    from agents.agent_one import main

    with patch.dict(os.environ, {"SUREIFY_AGENT_TOOL_ONLY": "1"}, clear=False):
        with patch("agents.agent_one.main.persist_event", return_value=False):
            main()
    # No exception = path works


# Agent two: tools return valid JSON; generate_product_recommendations emits event
def test_agent_two_get_current_database_context():
    """Agent two get_current_database_context returns JSON with expected keys."""
    from agents.agent_two.main import get_current_database_context

    out = get_current_database_context("Marty McFly")
    data = json.loads(out)
    assert "clients" in data
    assert "sureify_policies" in data
    assert "sureify_notifications_by_policy" in data or "contract_summary" in data


def test_agent_two_generate_recommendations_empty_changes():
    """Agent two generate_product_recommendations with {} returns valid output JSON."""
    from agents.agent_two.main import generate_product_recommendations

    out = generate_product_recommendations("{}", "Marty McFly")
    data = json.loads(out)
    assert "client_id" in data
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_agent_two_generate_recommendations_with_suitability():
    """Agent two with suitability changes returns recommendations and explanation."""
    from agents.agent_two.main import generate_product_recommendations

    changes = json.dumps({"suitability": {"riskTolerance": "moderate"}})
    out = generate_product_recommendations(changes, "Marty McFly")
    data = json.loads(out)
    assert "recommendations" in data
    assert "explanation" in data or "storable_payload" in data or "merged_profile_summary" in data


# Agent three: run_chat builds message and emits event; with mocked agent returns response
def test_agent_three_build_user_message():
    """Agent three build_user_message_for_agent includes screen state and user message."""
    from agents.agent_three.main import build_user_message_for_agent
    from agents.agent_three_schemas import ScreenState

    msg = build_user_message_for_agent(
        ScreenState.product_comparison, "Why did you recommend this?", "Marty McFly", None
    )
    assert "product_comparison" in msg
    assert "Why did you recommend this?" in msg
    assert "Marty McFly" in msg


def test_agent_three_run_chat_with_mocked_agent():
    """Agent three run_chat returns ChatResponse and persists event when agent is mocked."""
    from agents.agent_three.main import run_chat, create_agent_three

    mock_agent = MagicMock()
    mock_agent.return_value = {"output": "I can help with recommendations and explainability."}

    with patch("agents.agent_three.main.create_agent_three", return_value=mock_agent):
        with patch("agents.agent_three.main.persist_event", return_value=False) as mock_persist:
            response = run_chat(
                screen_state="elsewhere",
                user_message="What can you help me with?",
                client_id="Marty McFly",
            )
    assert response.reply == "I can help with recommendations and explainability."
    assert response.screen_state.value == "elsewhere"
    assert mock_persist.call_count == 1
    call_args = mock_persist.call_args[0][0]
    assert call_args.agent_id.value == "agent_three"
    assert call_args.success is True
    assert "elsewhere" in str(call_args.input_summary)


def test_agent_three_run_chat_emits_failure_event_on_exception():
    """Agent three run_chat persists failure event when agent raises."""
    from agents.agent_three.main import run_chat

    mock_agent = MagicMock()
    mock_agent.side_effect = RuntimeError("Simulated LLM failure")

    with patch("agents.agent_three.main.create_agent_three", return_value=mock_agent):
        with patch("agents.agent_three.main.persist_event", return_value=False) as mock_persist:
            with pytest.raises(RuntimeError, match="Simulated LLM failure"):
                run_chat("dashboard", "Hello", "Marty McFly")
    assert mock_persist.call_count == 1
    call_args = mock_persist.call_args[0][0]
    assert call_args.agent_id.value == "agent_three"
    assert call_args.success is False
    assert "Simulated LLM failure" in (call_args.error_message or "")
