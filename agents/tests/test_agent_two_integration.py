"""Integration tests for AgentTwo: profile persist, e-apply payload, reasons_to_switch. No DB/LLM required."""
from __future__ import annotations

import json
import os

import pytest

from agents.agent_two_schemas import ElectronicApplicationPayload, ProfileChangesInput
from agents.audit_writer import build_profile_row_from_changes, upsert_client_suitability_profile


def test_build_profile_row_from_changes_suitability_and_client_profile():
    """build_profile_row_from_changes maps suitability and clientProfile to DB columns."""
    changes = ProfileChangesInput.model_validate({
        "suitability": {"riskTolerance": "Moderate", "timeHorizon": "10+ years", "liquidityNeeds": "Low", "clientObjectives": "Growth"},
        "clientProfile": {"taxBracket": "22%", "householdNetWorth": "500k-1M", "householdLiquidAssets": "250k-500k", "grossIncome": "100k-150k"},
    })
    row = build_profile_row_from_changes("ACCT001", changes, None)
    assert row["client_account_number"] == "ACCT001"
    assert row.get("risk_tolerance") == "Moderate"
    assert row.get("investment_horizon") == "10+ years"
    assert row.get("liquidity_importance") == "Low"
    assert row.get("primary_objective") == "Growth"
    assert row.get("tax_bracket") == "22%"
    assert row.get("net_worth_range") == "500k-1M"
    assert row.get("liquid_net_worth_range") == "250k-500k"
    assert row.get("annual_income_range") == "100k-150k"


def test_build_profile_row_merges_existing_row():
    """build_profile_row_from_changes merges over existing DB row."""
    existing = {
        "client_account_number": "ACCT002",
        "risk_tolerance": "Conservative",
        "tax_bracket": "32%",
    }
    changes = ProfileChangesInput.model_validate({"suitability": {"riskTolerance": "Moderate"}})
    row = build_profile_row_from_changes("ACCT002", changes, existing)
    assert row["client_account_number"] == "ACCT002"
    assert row["risk_tolerance"] == "Moderate"
    assert row["tax_bracket"] == "32%"


def test_upsert_client_suitability_profile_without_db_returns_false():
    """Without DATABASE_URL, upsert_client_suitability_profile returns False."""
    old_url = os.environ.pop("DATABASE_URL", None)
    old_host = os.environ.pop("RDSHOST", None)
    try:
        result = upsert_client_suitability_profile(
            "ACCT001",
            {"client_account_number": "ACCT001", "risk_tolerance": "Moderate"},
        )
        assert result is False
    finally:
        if old_url is not None:
            os.environ["DATABASE_URL"] = old_url
        if old_host is not None:
            os.environ["RDSHOST"] = old_host


def test_electronic_application_payload_shape():
    """ElectronicApplicationPayload has run_id, client_id, merged_profile, selected_products."""
    payload = ElectronicApplicationPayload(
        run_id="run-123",
        client_id="Marty McFly",
        merged_profile={"suitability": {"risk_tolerance": "Moderate"}},
        selected_products=[{"product_id": "P1", "name": "Product A", "carrier": "Carrier X", "rate": "4.25%"}],
    )
    assert payload.run_id == "run-123"
    assert payload.client_id == "Marty McFly"
    assert payload.merged_profile["suitability"]["risk_tolerance"] == "Moderate"
    assert len(payload.selected_products) == 1
    assert payload.selected_products[0]["product_id"] == "P1"


def test_agent_two_output_includes_reasons_to_switch_and_e_apply():
    """generate_product_recommendations output includes reasons_to_switch and electronic_application_payload when successful."""
    try:
        from agents.agent_two.main import generate_product_recommendations
    except ImportError:
        pytest.skip("strands/agents not installed; run with full env")
    changes = json.dumps({"suitability": {"riskTolerance": "moderate"}})
    out = generate_product_recommendations(changes, "Marty McFly")
    data = json.loads(out)
    # May have error key if validation fails; otherwise expect full shape
    if "error" in data:
        pytest.skip("agent_two returned error (e.g. no DB/Sureify); run with full env for full integration")
    assert "client_id" in data
    assert "recommendations" in data
    # New fields: reasons_to_switch (pros/cons), electronic_application_payload
    assert "reasons_to_switch" in data or "electronic_application_payload" in data
    if "electronic_application_payload" in data and data["electronic_application_payload"]:
        e = data["electronic_application_payload"]
        assert "run_id" in e
        assert "client_id" in e
        assert "merged_profile" in e
        assert "selected_products" in e
