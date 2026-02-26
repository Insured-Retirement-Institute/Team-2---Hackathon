"""
AgentTwo: reads the database for current information, accepts JSON changes from the front-end
(suitability, client goals, client profile), and generates new product recommendations.

Run from repo root: PYTHONPATH=. uv run python -m agents.agent_two
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
_env_file = _repo_root / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

from strands import Agent, tool

from agents.logging_config import get_logger

logger = get_logger(__name__)

from agents.agent_two_schemas import AgentTwoStorablePayload, ProductRecommendationsOutput, ProfileChangesInput
from agents.agent_two_schemas import (
    AgentTwoStorablePayload,
    BestInterestSummary,
    CustomerSelection,
    ElectronicApplicationPayload,
    FinalEAppOutput,
    ProductRecommendationsOutput,
    ProfileChangesInput,
)
from agents.audit_writer import (
    build_profile_row_from_changes,
    persist_agent_two_payload,
    persist_event,
    upsert_client_suitability_profile,
)
import httpx

from agents.db_reader import get_current_database_context as fetch_db_context
from agents.recommendations import generate_recommendations
from agents.responsible_ai_schemas import AgentId, AgentRunEvent

_API_BASE = os.environ.get("API_BASE_URL", "")
if not _API_BASE:
    raise RuntimeError("API_BASE_URL environment variable is required but not set")


def _api_get(path: str) -> list | dict:
    """GET helper for the API server passthrough endpoints."""
    import time
    url = f"{_API_BASE}{path}"
    logger.info("API GET %s starting...", url)
    start = time.time()
    r = httpx.get(url, timeout=90)
    elapsed = time.time() - start
    logger.info("API GET %s -> %d in %.2fs", url, r.status_code, elapsed)
    r.raise_for_status()
    return r.json()


def _client_profile_characteristics(merged: dict) -> list[str]:
    """Extract client profile characteristics from merged_profile_summary for Best Interest narrative."""
    parts: list[str] = []
    suit = merged.get("suitability") or {}
    goals = merged.get("goals_and_profile") or {}
    if suit.get("risk_tolerance"):
        parts.append(f"risk tolerance: {suit['risk_tolerance']}")
    if suit.get("time_horizon") or suit.get("investment_horizon"):
        parts.append(f"time horizon: {suit.get('time_horizon') or suit.get('investment_horizon')}")
    if suit.get("liquidity_needs") or suit.get("liquidity_importance"):
        parts.append(f"liquidity needs: {suit.get('liquidity_needs') or suit.get('liquidity_importance')}")
    if suit.get("client_objectives"):
        parts.append(f"objectives: {suit['client_objectives']}")
    if goals.get("financial_objectives"):
        parts.append(f"financial objectives: {goals['financial_objectives']}")
    if goals.get("distribution_plan"):
        parts.append(f"distribution plan: {goals['distribution_plan']}")
    if goals.get("expected_holding_period"):
        parts.append(f"expected holding period: {goals['expected_holding_period']}")
    if goals.get("gross_income"):
        parts.append(f"gross income: {goals['gross_income']}")
    if goals.get("household_net_worth"):
        parts.append(f"household net worth: {goals['household_net_worth']}")
    if goals.get("household_liquid_assets"):
        parts.append(f"household liquid assets: {goals['household_liquid_assets']}")
    if goals.get("tax_bracket"):
        parts.append(f"tax bracket: {goals['tax_bracket']}")
    return parts


def _selection_context(
    recommendations: list,
    customer_selection: CustomerSelection | None,
) -> tuple[str, list[dict]]:
    """
    Build a human-readable sentence for the customer's selection and the list of selected
    recommendation dicts (for e-app). Returns (selection_sentence, selected_recs).
    """
    if not customer_selection or not getattr(customer_selection, "selected_product_ids", None):
        return "", []
    ids = set(customer_selection.selected_product_ids or [])
    if not ids:
        return "", []
    selected: list[dict] = []
    names: list[str] = []
    for r in recommendations:
        if r.product_id in ids:
            selected.append({
                "product_id": r.product_id,
                "name": r.name,
                "carrier": r.carrier,
                "rate": r.rate,
                "term": r.term,
                "surrenderPeriod": r.surrenderPeriod,
                "freeWithdrawal": r.freeWithdrawal,
                "guaranteedMinRate": r.guaranteedMinRate,
                "match_reason": r.match_reason,
            })
            names.append(f"{r.name} ({r.carrier})" if r.carrier else r.name)
    if not names:
        return "", []
    selection_sentence = (
        "The customer selected "
        + (", ".join(names) if len(names) <= 3 else ", ".join(names[:2]) + f", and {len(names) - 2} other(s)")
        + " from the opportunities presented."
    )
    if getattr(customer_selection, "notes", None) and customer_selection.notes.strip():
        selection_sentence += f" Notes: {customer_selection.notes.strip()}"
    return selection_sentence, selected


def _build_best_interest_and_eapp(
    run_id: str,
    created_at: str,
    client_id: str,
    out: ProductRecommendationsOutput,
    e_apply: ElectronicApplicationPayload,
    customer_selection: CustomerSelection | None = None,
) -> tuple[BestInterestSummary, FinalEAppOutput]:
    """Build Best Interest Combined Framework summary and final e-app output from recommendation result."""
    expl = out.explanation
    summary_text = expl.summary if expl else "Opportunities presented from product catalog and client context."
    criteria = (expl.choice_criteria or []) if expl else []
    data_sources = (expl.data_sources_used or []) if expl else []
    selection_sentence, selected_recs = _selection_context(out.recommendations, customer_selection)
    recs_with_explain = [
        {
            "product_id": r.product_id,
            "name": r.name,
            "carrier": r.carrier,
            "rate": r.rate,
            "term": r.term,
            "surrenderPeriod": r.surrenderPeriod,
            "freeWithdrawal": r.freeWithdrawal,
            "guaranteedMinRate": r.guaranteedMinRate,
            "match_reason": r.match_reason,
        }
        for r in out.recommendations
    ]
    merged = out.merged_profile_summary or {}
    profile_chars = _client_profile_characteristics(merged)
    profile_narrative = (
        "Client profile characteristics used to justify the assessment: "
        + "; ".join(profile_chars)
        + "."
        if profile_chars
        else "Client profile characteristics were considered where provided."
    )
    # Human-readable data sources (no internal names like sureify_products, db_suitability)
    _source_labels = {
        "sureify_products": "available product catalog",
        "db_products": "product catalog",
        "db_suitability": "client suitability profile",
    }
    data_sources_readable = [_source_labels.get(s, s) for s in data_sources] or ["product catalog and client profile"]
    sources_phrase = ", ".join(data_sources_readable)
    # Summary for display: use "Opportunity Generator" and "opportunities presented"
    summary_display = (summary_text or "").replace("AgentTwo", "Opportunity Generator").replace("agentTwo", "Opportunity Generator")
    summary_display = summary_display.replace("recommendation(s)", "opportunities presented")
    if selection_sentence:
        summary_display = summary_display.rstrip(". ") + ". " + selection_sentence

    prudential = (
        f"Reasonable diligence was applied to the customer's financial situation, needs, and objectives. "
        f"{profile_narrative} "
        f"Available products were investigated from the {sources_phrase}. "
        f"Explicit comparative analysis was performed using criteria: {', '.join(criteria) or 'product match'}. "
        f"Summary: {summary_display}"
    )
    if selection_sentence:
        prudential = selection_sentence + " " + prudential
    conflict = (
        "Material conflicts of interest are identified in firm disclosures. "
        "Compensation structures (commission, fee) are disclosed; conflicts are eliminated where possible or disclosed in writing. "
        "The opportunities presented were generated using the client profile characteristics above and product data; no conflict incentivized the selection of a particular product."
    )
    if selection_sentence:
        conflict = selection_sentence + " " + conflict
    _chars_ref = ", ".join(profile_chars[:6]) + ("..." if len(profile_chars) > 6 else "") if profile_chars else "suitability and goals"
    transparency = (
        "Conflicts of interest and compensation are disclosed in writing before the transaction. "
        f"Product alternatives considered are reflected in the opportunities presented and reasons to switch (pros/cons). "
        f"The client profile characteristics that justify the assessment ({_chars_ref}) are documented in merged_profile_summary. "
        "Product risks and features (rate, term, surrender period, free withdrawal, guaranteed minimum) are included for each opportunity with match_reason explaining fit to the client's profile."
    )
    if selection_sentence:
        transparency = selection_sentence + " " + transparency
    documentation = (
        f"Customer information gathered and analysis performed are documented in merged_profile_summary and input_summary, including the client profile characteristics that justify the assessment: {', '.join(profile_chars) if profile_chars else 'suitability and goals'}. "
        "The basis for the opportunities presented is documented in explanation (summary, data_sources_used, choice_criteria) and in each opportunity's match_reason. "
        "Alternatives considered are reflected in the product set and reasons_to_switch. "
    )
    if selection_sentence:
        documentation += "The customer's selection from the opportunities presented is documented in this summary and in the selected_products submitted for e-app. "
    documentation += (
        "Records supporting compliance (run_id, timestamp, payload) are retained; minimum 6-year retention applies per firm policy. "
        "Customer acknowledgment of the opportunities presented and conflicts is obtained at point of sale (e-app flow)."
    )
    ongoing = (
        "Firm will monitor customer accounts and the opportunities presented for continued suitability; "
        "review changing circumstances and market conditions; update the opportunities presented when customer profile characteristics change; "
        "and conduct periodic compliance reviews of firm-wide practices."
    )

    best_interest = BestInterestSummary(
        prudential_standards=prudential,
        conflict_management=conflict,
        transparency=transparency,
        documentation=documentation,
        ongoing_duty=ongoing,
    )
    # When customer selected specific products, final e-app shows only those
    recs_for_eapp = selected_recs if selected_recs else recs_with_explain
    final_eapp = FinalEAppOutput(
        run_id=run_id,
        created_at=created_at,
        client_id=client_id,
        best_interest_summary=best_interest,
        recommendations_with_explainability=recs_for_eapp,
        reasons_to_switch=out.reasons_to_switch,
        electronic_application_payload=e_apply,
        customer_acknowledgment_placeholder="Customer acknowledgment of recommendations and conflicts to be obtained at point of sale.",
    )
    return best_interest, final_eapp


def _get_sureify_context(customer_identifier: str) -> dict:
    """Fetch context from passthrough APIs and the client profile endpoint."""
    policies = _api_get("/passthrough/policy-data")
    products = _api_get("/passthrough/product-options")
    alerts = _api_get("/api/alerts")

    # Fetch structured client profile (DB-first with Sureify fallback)
    try:
        client_profile = _api_get(f"/api/clients/{customer_identifier}/profile")
    except Exception:
        logger.warning("Failed to fetch client profile for %s, falling back to empty", customer_identifier)
        client_profile = {}

    # Extract suitability from profile response for backward compatibility
    suitability_data = client_profile.get("suitability") or {}

    notifications_by_policy: dict[str, list] = {}
    for a in alerts:
        pid = a.get("policyId") or a.get("policy_id") or ""
        if pid:
            notifications_by_policy.setdefault(pid, []).append(a)
    return {
        "sureify_policies": policies,
        "sureify_notifications_by_policy": notifications_by_policy,
        "sureify_products": products,
        "sureify_suitability_data": suitability_data,
        "client_profile": client_profile,
    }


@tool
def get_current_database_context(client_id: str = "") -> str:
    """
    Read all current information: from the database (clients, suitability profiles,
    contract_summary, products) and from the API server (policies, products,
    client profile with suitability, notifications).
    client_id: optional; used for DB contract_summary filter and client profile lookup.
    Returns JSON with keys: clients, client_suitability_profiles, contract_summary, products,
    sureify_policies, sureify_notifications_by_policy, sureify_products,
    sureify_suitability_data, client_profile.
    """
    ctx = fetch_db_context(client_id or None)
    cid = (client_id or "").strip()
    if not cid:
        logger.warning("get_current_database_context called without client_id")
    sureify = _get_sureify_context(cid or "unknown")
    ctx["sureify_policies"] = sureify["sureify_policies"]
    ctx["sureify_notifications_by_policy"] = sureify["sureify_notifications_by_policy"]
    ctx["sureify_products"] = sureify["sureify_products"]
    ctx["sureify_suitability_data"] = sureify["sureify_suitability_data"]
    ctx["client_profile"] = sureify["client_profile"]
    return json.dumps(ctx, default=str, indent=2)


@tool
def generate_product_recommendations(
    changes_json: str,
    client_id: str,
    alert_id: str = "",
) -> str:
    """
    Take JSON from the front-end with changes to suitability, client goals, and/or client profile;
    merge with current DB state; and generate new product recommendations.
    changes_json: JSON object with optional keys "suitability", "clientGoals", "clientProfile".
    client_id: client identifier. alert_id: optional IRI alert ID.
    Returns JSON: ProductRecommendationsOutput (recommendations, explanation, storable_payload, ...).
    """
    run_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    event_id = str(uuid.uuid4())
    client_id_scope = client_id

    def _emit_event(
        input_summary: dict,
        success: bool,
        error_message: str | None = None,
        explanation_summary: str | None = None,
        data_sources_used: list[str] | None = None,
        choice_criteria: list[str] | None = None,
        input_validation_passed: bool | None = None,
        payload_ref: str | None = None,
    ) -> None:
        event = AgentRunEvent(
            event_id=event_id,
            timestamp=created_at,
            agent_id=AgentId.agent_two,
            run_id=run_id,
            client_id_scope=client_id_scope,
            input_summary=input_summary,
            success=success,
            error_message=error_message,
            explanation_summary=explanation_summary,
            data_sources_used=data_sources_used,
            choice_criteria=choice_criteria,
            input_validation_passed=input_validation_passed,
            guardrail_triggered=None,
            payload_ref=payload_ref,
        )
        persist_event(event)

    try:
        payload = json.loads(changes_json)
    except json.JSONDecodeError as e:
        logger.error("generate_product_recommendations: invalid JSON input: %s", e)
        _emit_event({}, False, error_message=str(e), input_validation_passed=False)
        return json.dumps({"error": "Invalid JSON", "message": str(e)})

    input_summary = {"sections_present": [k for k in ("suitability", "clientGoals", "clientProfile", "customerSelection") if payload.get(k)]}

    try:
        changes = ProfileChangesInput.model_validate(payload)
    except Exception as e:
        logger.error("generate_product_recommendations: invalid changes shape: %s", e)
        _emit_event(input_summary, False, error_message=str(e), input_validation_passed=False)
        return json.dumps({"error": "Invalid changes shape", "message": str(e)})

    db_context = fetch_db_context(client_id)
    cid = (client_id or "").strip() or "unknown"
    sureify = _get_sureify_context(cid)
    db_context["sureify_policies"] = sureify["sureify_policies"]
    db_context["sureify_notifications_by_policy"] = sureify["sureify_notifications_by_policy"]
    db_context["sureify_products"] = sureify["sureify_products"]
    db_context["sureify_suitability_data"] = sureify["sureify_suitability_data"]
    db_context["client_profile"] = sureify["client_profile"]

    # Persist front-end client profile when new or as update (upsert)
    if changes.client_profile or changes.suitability:
        clients = db_context.get("clients") or []
        profiles = db_context.get("client_suitability_profiles") or []
        client_row = None
        for c in clients:
            acct = (c.get("client_account_number") or "").strip()
            name = (c.get("client_name") or "").lower()
            if acct == client_id or (client_id and (client_id.lower() in name or client_id in acct)):
                client_row = c
                break
        if not client_row and clients:
            client_row = clients[0]
        acct = (client_row or {}).get("client_account_number")
        if acct:
            existing = next(
                (p for p in profiles if p.get("client_account_number") == acct),
                None,
            )
            profile_row = build_profile_row_from_changes(acct, changes, existing)
            if len(profile_row) > 1:  # more than just client_account_number
                upsert_client_suitability_profile(acct, profile_row)

    iri_result: dict | None = None
    if alert_id and os.environ.get("IRI_API_BASE_URL"):
        try:
            from agents.iri_client import (
                run_iri_comparison,
                save_iri_client_profile,
                save_iri_suitability,
            )
            if changes.client_profile:
                params = changes.client_profile.model_dump(exclude_none=True)
                logger.debug("Saving client profile to IRI API: client_id=%s", client_id)
                save_iri_client_profile(client_id, params)
            if changes.suitability:
                suit = changes.suitability.model_dump(exclude_none=True)
                logger.debug("Saving suitability to IRI API: alert_id=%s", alert_id)
                save_iri_suitability(alert_id, suit)
            logger.debug("Running IRI comparison: alert_id=%s", alert_id)
            iri_result = run_iri_comparison(alert_id)
        except Exception:
            logger.exception("IRI API operations failed for alert_id=%s", alert_id)

    try:
        out = generate_recommendations(
            client_id=client_id,
            db_context=db_context,
            changes=changes,
            alert_id=alert_id or None,
            iri_comparison_result=iri_result,
        )
    except Exception as e:
        logger.exception("generate_product_recommendations: recommendation generation failed for client_id=%s", client_id)
        _emit_event(input_summary, False, error_message=str(e), input_validation_passed=True)
        raise

    # Build submission-ready e-apply payload (merged profile + selected products)
    merged = out.merged_profile_summary or {}
    _, selected_for_eapp = _selection_context(out.recommendations, getattr(changes, "customer_selection", None))
    selected = selected_for_eapp if selected_for_eapp else [r.model_dump(mode="json") for r in out.recommendations]
    e_apply = ElectronicApplicationPayload(
        run_id=run_id,
        client_id=client_id,
        merged_profile=merged,
        selected_products=selected,
    )
    out.electronic_application_payload = e_apply

    # Best Interest Combined Framework summary and final e-app output (contextualized with customer selection when provided)
    best_interest, final_eapp = _build_best_interest_and_eapp(
        run_id, created_at, client_id, out, e_apply, customer_selection=getattr(changes, "customer_selection", None)
    )
    out.best_interest_summary = best_interest
    out.final_eapp_output = final_eapp

    if out.explanation:
        storable = AgentTwoStorablePayload(
            run_id=run_id,
            created_at=created_at,
            client_id=client_id,
            input_summary=input_summary,
            explanation=out.explanation,
            recommendations=out.recommendations,
            reasons_to_switch=out.reasons_to_switch,
            merged_profile_summary=out.merged_profile_summary,
            iri_comparison_result=out.iri_comparison_result,
            electronic_application_payload=e_apply,
        )
        out.storable_payload = storable
        payload_ref_id = persist_agent_two_payload(
            run_id=run_id,
            created_at=created_at,
            client_id=client_id,
            payload=storable.model_dump(mode="json"),
        )
        _emit_event(
            input_summary,
            True,
            explanation_summary=out.explanation.summary,
            data_sources_used=out.explanation.data_sources_used or None,
            choice_criteria=out.explanation.choice_criteria or None,
            input_validation_passed=True,
            payload_ref=payload_ref_id,
        )
    else:
        _emit_event(input_summary, True, input_validation_passed=True)
    return out.model_dump_json(indent=2, exclude_none=True)


AGENT_TWO_SYSTEM_PROMPT = """You are agentTwo: you read the database for all current information (clients, suitability profiles, contracts, products) and use JSON changes from the front-end to generate new product recommendations.

Your workflow:
1. **Read current state:** Use `get_current_database_context` with an optional client_id to load clients, client_suitability_profiles, contract_summary, and products from the database.
2. **Apply changes and get recommendations:** When the user provides a JSON payload with changes to suitability, client goals, or client profile, call `generate_product_recommendations` with that JSON, the client_id, and optionally an alert_id. The tool merges the changes with current DB data and returns product recommendations (and optionally IRI comparison result if alert_id and IRI API are configured).

Front-end changes JSON shape:
- **suitability** (optional): riskTolerance, timeHorizon, liquidityNeeds, clientObjectives, etc.
- **clientGoals** (optional): financialObjectives, distributionPlan, expectedHoldingPeriod, etc.
- **clientProfile** (optional): grossIncome, householdNetWorth, taxBracket, etc.

Output: Return the full product recommendations JSON to the user (recommendations array, merged_profile_summary, and iri_comparison_result if present).
"""


def create_agent_two() -> Agent:
    """Create the Strands agent for agentTwo."""
    logger.debug("Creating agent_two Strands agent with Bedrock")
    return Agent(
        tools=[get_current_database_context, generate_product_recommendations],
        system_prompt=AGENT_TWO_SYSTEM_PROMPT,
    )


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="AgentTwo: DB + changes → product recommendations")
    parser.add_argument("--changes", type=str, help="Path to JSON file with suitability/clientGoals/clientProfile changes")
    parser.add_argument("--client-id", type=str, default="1001", help="Client identifier (Sureify UserID; use 1001 for live API data)")
    parser.add_argument("--alert-id", type=str, default="", help="Optional IRI alert ID for comparison")
    parser.add_argument("--tool-only", action="store_true", help="Run tools only (no LLM)")
    args = parser.parse_args()

    if args.tool_only:
        ctx = get_current_database_context(args.client_id)
        print(ctx)
        if args.changes:
            path = Path(args.changes)
            if path.exists():
                changes_json = path.read_text()
                print("\n--- Recommendations ---\n")
                print(generate_product_recommendations(changes_json, args.client_id, args.alert_id))
        return

    agent = create_agent_two()
    if args.changes:
        path = Path(args.changes)
        changes_json = path.read_text() if path.exists() else "{}"
        user_message = (
            f"Get current database context for client_id '{args.client_id}', "
            f"then generate product recommendations using this changes JSON:\n{changes_json}"
        )
    else:
        user_message = (
            f"Get current database context for client_id '{args.client_id}' and summarize what's in the database. "
            "Then explain that I can send a JSON with changes to suitability, client goals, or client profile to get new product recommendations."
        )
    result = agent(user_message)
    print(result.get("output", result) if isinstance(result, dict) else result)


if __name__ == "__main__":
    main()
