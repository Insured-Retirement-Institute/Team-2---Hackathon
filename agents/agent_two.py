"""
AgentTwo: reads the database for current information, accepts JSON changes from the front-end
(suitability, client goals, client profile), and generates new product recommendations.

Run from repo root:
  PYTHONPATH=. uv run python -m agents.agent_two
Or with a changes JSON file:
  PYTHONPATH=. uv run python -m agents.agent_two --changes changes.json --client-id "Marty McFly"
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

_env_file = _repo_root / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass

from strands import Agent, tool

from agents.agent_two_schemas import AgentTwoStorablePayload, ProductRecommendationsOutput, ProfileChangesInput
from agents.db_reader import get_current_database_context as fetch_db_context
from agents.recommendations import generate_recommendations
from agents.sureify_client import get_book_of_business as fetch_sureify_policies
from agents.sureify_client import get_notifications_for_policies as fetch_sureify_notifications
from agents.sureify_client import get_products as fetch_sureify_products


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


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
    client_id: optional; used for DB contract_summary filter and as Sureify customer_identifier
               (e.g. "Marty McFly"). If empty, Sureify uses "Marty McFly" for mock data.
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
    changes_json: JSON object with optional keys "suitability", "clientGoals", "clientProfile"
                  (each optional; only include changed fields).
    client_id: client identifier (e.g. client_account_number or client name).
    alert_id: optional; if provided and IRI_API_BASE_URL is set, save profile/suitability to IRI
              and run comparison for this alert, then include IRI comparison in the result.
    Returns JSON: ProductRecommendationsOutput (client_id, merged_profile_summary, recommendations, explanation, storable_payload for DB, iri_comparison_result).
    """
    try:
        payload = json.loads(changes_json)
    except json.JSONDecodeError as e:
        return json.dumps({"error": "Invalid JSON", "message": str(e)})

    try:
        changes = ProfileChangesInput.model_validate(payload)
    except Exception as e:
        return json.dumps({"error": "Invalid changes shape", "message": str(e)})

    db_context = fetch_db_context(client_id)
    sureify_id = client_id.strip() if client_id else "Marty McFly"
    sureify = _get_sureify_context(sureify_id)
    db_context["sureify_policies"] = sureify["sureify_policies"]
    db_context["sureify_notifications_by_policy"] = sureify["sureify_notifications_by_policy"]
    db_context["sureify_products"] = sureify["sureify_products"]

    iri_result: dict | None = None
    if alert_id and os.environ.get("IRI_API_BASE_URL"):
        try:
            from agents.iri_client import (
                get_iri_client_profile,
                run_iri_comparison,
                save_iri_client_profile,
                save_iri_suitability,
            )
            # Optionally push changes to IRI and run comparison
            if changes.client_profile:
                params = changes.client_profile.model_dump(exclude_none=True)
                save_iri_client_profile(client_id, params)
            if changes.suitability:
                suit = changes.suitability.model_dump(exclude_none=True)
                save_iri_suitability(alert_id, suit)
            iri_result = run_iri_comparison(alert_id)
        except Exception:
            pass  # continue with local recommendations even if IRI fails

    out = generate_recommendations(
        client_id=client_id,
        db_context=db_context,
        changes=changes,
        alert_id=alert_id or None,
        iri_comparison_result=iri_result,
    )
    # Build storable payload for database (run_id, created_at, explanation, recommendations)
    input_summary = {
        "sections_present": [k for k in ("suitability", "clientGoals", "clientProfile") if payload.get(k)],
    }
    if out.explanation:
        storable = AgentTwoStorablePayload(
            run_id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            client_id=client_id,
            input_summary=input_summary,
            explanation=out.explanation,
            recommendations=out.recommendations,
            merged_profile_summary=out.merged_profile_summary,
            iri_comparison_result=out.iri_comparison_result,
        )
        out.storable_payload = storable
    return out.model_dump_json(indent=2, exclude_none=True)


# ---------------------------------------------------------------------------
# System prompt and agent
# ---------------------------------------------------------------------------

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
    parser.add_argument("--tool-only", action="store_true", help="Run tools only (no LLM): DB context then recommendations if --changes given")
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
