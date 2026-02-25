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
    ElectronicApplicationPayload,
    ProductRecommendationsOutput,
    ProfileChangesInput,
)
from agents.audit_writer import (
    build_profile_row_from_changes,
    persist_agent_two_payload,
    persist_event,
    upsert_client_suitability_profile,
)
from agents.db_reader import get_current_database_context as fetch_db_context
from agents.recommendations import generate_recommendations
from agents.responsible_ai_schemas import AgentId, AgentRunEvent
from agents.sureify_client import get_book_of_business as fetch_sureify_policies
from agents.sureify_client import get_notifications_for_policies as fetch_sureify_notifications
from agents.sureify_client import get_products as fetch_sureify_products


def _get_sureify_context(customer_identifier: str) -> dict:
    """Fetch book of business, notifications, and products from Sureify (or mock when not configured)."""
    policies = fetch_sureify_policies(customer_identifier)
    policy_ids = [p.get("ID") or p.get("policyNumber") or "" for p in policies if p]
    policy_ids = [x for x in policy_ids if x]
    notifications = fetch_sureify_notifications(policy_ids, user_id=customer_identifier)
    products = fetch_sureify_products(customer_identifier)
    return {
        "sureify_policies": policies,
        "sureify_notifications_by_policy": notifications,
        "sureify_products": products,
    }


@tool
def get_current_database_context(client_id: str = "") -> str:
    """
    Read all current information: from the database (clients, suitability profiles,
    contract_summary, products) and from Sureify (book of business / policies and notifications).
    client_id: optional; used for DB contract_summary filter and as Sureify customer_identifier.
    Returns JSON with keys: clients, client_suitability_profiles, contract_summary, products,
    sureify_policies, sureify_notifications_by_policy, sureify_products.
    """
    ctx = fetch_db_context(client_id or None)
    sureify_id = client_id.strip() if client_id else "Marty McFly"
    sureify = _get_sureify_context(sureify_id)
    ctx["sureify_policies"] = sureify["sureify_policies"]
    ctx["sureify_notifications_by_policy"] = sureify["sureify_notifications_by_policy"]
    ctx["sureify_products"] = sureify["sureify_products"]
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

    input_summary = {"sections_present": [k for k in ("suitability", "clientGoals", "clientProfile") if payload.get(k)]}

    try:
        changes = ProfileChangesInput.model_validate(payload)
    except Exception as e:
        logger.error("generate_product_recommendations: invalid changes shape: %s", e)
        _emit_event(input_summary, False, error_message=str(e), input_validation_passed=False)
        return json.dumps({"error": "Invalid changes shape", "message": str(e)})

    db_context = fetch_db_context(client_id)
    sureify_id = client_id.strip() if client_id else "Marty McFly"
    sureify = _get_sureify_context(sureify_id)
    db_context["sureify_policies"] = sureify["sureify_policies"]
    db_context["sureify_notifications_by_policy"] = sureify["sureify_notifications_by_policy"]
    db_context["sureify_products"] = sureify["sureify_products"]

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
    selected = [r.model_dump(mode="json") for r in out.recommendations]
    e_apply = ElectronicApplicationPayload(
        run_id=run_id,
        client_id=client_id,
        merged_profile=merged,
        selected_products=selected,
    )
    out.electronic_application_payload = e_apply

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
    parser.add_argument("--client-id", type=str, default="Marty McFly", help="Client identifier")
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
