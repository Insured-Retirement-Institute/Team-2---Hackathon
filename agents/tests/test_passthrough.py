"""Tests for passthrough API integration: imports, inline httpx calls, normalizers."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Import tests -- verify all three agent modules import without errors
# ---------------------------------------------------------------------------

def test_agent_one_imports_cleanly():
    import agents.agent_one.main  # noqa: F401


def test_agent_two_imports_cleanly():
    import agents.agent_two.main  # noqa: F401


def test_agent_three_imports_cleanly():
    import agents.agent_three.main  # noqa: F401


# ---------------------------------------------------------------------------
# Normalizer tests (inline helpers in agent_one and agent_two)
# ---------------------------------------------------------------------------

def test_normalize_policies_string_id():
    from agents.agent_one.main import _normalize_policies
    result = _normalize_policies([{"ID": 123, "name": "Policy A"}])
    assert result == [{"ID": "123", "name": "Policy A"}]


def test_normalize_policies_already_string():
    from agents.agent_one.main import _normalize_policies
    result = _normalize_policies([{"ID": "abc", "name": "Policy B"}])
    assert result == [{"ID": "abc", "name": "Policy B"}]


def test_normalize_product_options_canonical_keys():
    from agents.agent_one.main import _normalize_product_options
    raw = [{"productId": "P1", "name": "Flex MYGA", "carrier": "Athene", "rate": "4.25%"}]
    result = _normalize_product_options(raw)
    assert len(result) == 1
    assert result[0]["product_id"] == "P1"
    assert result[0]["name"] == "Flex MYGA"
    assert result[0]["carrier"] == "Athene"
    assert result[0]["rate"] == "4.25%"


def test_normalize_product_options_numeric_rate():
    from agents.agent_one.main import _normalize_product_options
    raw = [{"ID": "X", "name": "Test", "carrier": "C", "rate": 3.5}]
    result = _normalize_product_options(raw)
    assert result[0]["rate"] == "3.5%"


def test_normalize_product_options_missing_rate():
    from agents.agent_one.main import _normalize_product_options
    raw = [{"ID": "X", "name": "Test", "carrier": "C"}]
    result = _normalize_product_options(raw)
    assert result[0]["rate"] == "N/A"


def test_normalize_notes_groups_by_policy():
    from agents.agent_one.main import _normalize_notes_to_notifications
    notes = [
        {"policyID": "P1", "title": "Note 1"},
        {"policyID": "P2", "content": "Note 2"},
        {"policyID": "P1", "title": "Note 3"},
        {"policyID": "UNKNOWN", "title": "Orphan"},
    ]
    result = _normalize_notes_to_notifications(notes, ["P1", "P2"])
    assert len(result["P1"]) == 2
    assert len(result["P2"]) == 1
    assert result["P1"][0]["message"] == "Note 1"
    assert result["P2"][0]["message"] == "Note 2"
    assert result["P1"][0]["type"] == "note"
    assert result["P1"][0]["severity"] == "info"


def test_normalize_notes_empty():
    from agents.agent_one.main import _normalize_notes_to_notifications
    result = _normalize_notes_to_notifications([], ["P1"])
    assert result == {"P1": []}


# ---------------------------------------------------------------------------
# Passthrough GET tests (mocked httpx)
# ---------------------------------------------------------------------------

def _mock_httpx_response(json_data, status_code=200):
    """Create a mock httpx.Response."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


def test_agent_one_passthrough_get_policies():
    from agents.agent_one.main import _passthrough_get
    fake_policies = [{"ID": "P1", "name": "Policy A"}]
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = _mock_httpx_response(fake_policies)

    with patch("agents.agent_one.main.httpx.Client", return_value=mock_client):
        result = _passthrough_get("/policies", {"user_id": "1001"})

    assert result == fake_policies
    call_args = mock_client.get.call_args
    assert "/passthrough/policies" in call_args[0][0]


def test_agent_two_get_sureify_context_calls_all_endpoints():
    from agents.agent_two.main import _get_sureify_context
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = _mock_httpx_response([])

    with patch("agents.agent_two.main.httpx.Client", return_value=mock_client):
        result = _get_sureify_context("1001")

    called_urls = [call[0][0] for call in mock_client.get.call_args_list]
    expected_paths = ["/policies", "/notes", "/product-options", "/suitability-data", "/client-profiles"]
    for path in expected_paths:
        assert any(path in url for url in called_urls), f"Expected {path} in called URLs: {called_urls}"

    assert "sureify_policies" in result
    assert "sureify_notifications_by_policy" in result
    assert "sureify_products" in result
    assert "sureify_suitability_data" in result
    assert "sureify_client_profiles" in result


def test_passthrough_get_failure_returns_empty():
    from agents.agent_one.main import _passthrough_get
    import httpx as _httpx
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.side_effect = _httpx.ConnectError("Connection refused")

    with patch("agents.agent_one.main.httpx.Client", return_value=mock_client):
        result = _passthrough_get("/policies")

    assert result == []


def test_agent_one_get_book_of_business_mocked():
    from agents.agent_one.main import get_book_of_business
    fake = [{"ID": "P1", "clientName": "Marty McFly"}]
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.get.return_value = _mock_httpx_response(fake)

    with patch("agents.agent_one.main.httpx.Client", return_value=mock_client):
        result_json = get_book_of_business("Marty McFly")

    data = json.loads(result_json)
    assert isinstance(data, list)
    assert data[0]["ID"] == "P1"
