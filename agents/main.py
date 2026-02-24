<<<<<<< HEAD
def main():
    print("Hello from agents!")
=======
"""
Strands agent: Sureify book of business for Marty McFly.

Scans Sureify APIs (or mock), lists all policies as JSON using frontend-relevant
shapes, attaches notifications, and applies business logic (replacements,
data quality, income activation, scheduled-meeting recommendation).

Run from repo root with PYTHONPATH including repo root so api.src.api is importable:
  PYTHONPATH=. uv run python agents/main.py
  or: cd agents && uv run python main.py  (with agents in path)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure repo root is on path for api.src.api when running as script
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Load .env from repo root so AWS_* and SUREIFY_* are available
_env_file = _repo_root / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        pass  # optional: run with env vars set manually or via shell

# Use Bedrock native (IAM) auth: boto3 uses AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
# or ~/.aws/credentials (aws configure). Bearer token is not used.
import os as _os
_os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)

from strands import Agent, tool

from agents.logic import apply_business_logic
from agents.schemas import BookOfBusinessOutput, PolicyNotification, PolicyOutput
from agents.sureify_client import get_book_of_business as fetch_policies
from agents.sureify_client import get_notifications_for_policies as fetch_notifications


# ---------------------------------------------------------------------------
# Tools (Strands @tool)
# ---------------------------------------------------------------------------


@tool
def get_book_of_business(customer_identifier: str) -> str:
    """
    Get the book of business (all policies) for a customer or advisor from Sureify.

    Use this when you need to list all policies for a given customer, e.g. Marty McFly.
    Returns a JSON list of policy objects (policy numbers, carrier, status, product, etc.).
    """
    policies = fetch_policies(customer_identifier)
    return json.dumps(policies, default=str, indent=2)


@tool
def get_notifications_for_policies(policy_ids: str) -> str:
    """
    Get notifications applicable to the given policies.

    Use this to fetch notifications for the policy IDs returned by get_book_of_business.
    policy_ids: JSON array of policy ID strings, e.g. '["pol-marty-001", "pol-marty-002"]'
    Returns a JSON object mapping each policy_id to a list of notifications (type, message, severity).
    """
    try:
        ids = json.loads(policy_ids)
    except json.JSONDecodeError:
        return json.dumps({"error": "policy_ids must be a JSON array of strings"})
    if not isinstance(ids, list):
        return json.dumps({"error": "policy_ids must be a JSON array"})
    result = fetch_notifications(ids)
    return json.dumps(result, default=str, indent=2)


@tool
def get_book_of_business_with_notifications_and_flags(customer_identifier: str) -> str:
    """
    Get the full book of business for a customer with notifications and business logic flags.

    Use this to produce the complete output for Marty McFly: all policies in JSON form
    (aligned with sureify_models for the frontend), plus for each policy: applicable
    notifications, replacement_opportunity, data_quality_issues, income_activation_eligible,
    and schedule_meeting recommendation. Returns a single JSON object with customer_identifier
    and policies array, ready for the frontend.
    """
    policies = fetch_policies(customer_identifier)
    if not policies:
        out = BookOfBusinessOutput(customer_identifier=customer_identifier, policies=[])
        return out.model_dump_json(indent=2)

    policy_ids = [p.get("ID") or p.get("policyNumber") or "" for p in policies]
    policy_ids = [x for x in policy_ids if x]
    notif_by_policy = fetch_notifications(policy_ids)

    outputs: list[PolicyOutput] = []
    for p in policies:
        pid = p.get("ID") or p.get("policyNumber") or ""
        logic = apply_business_logic(p)
        notifs = notif_by_policy.get(pid) or []
        notifications = [
            PolicyNotification(
                notification_type=n.get("type", "unknown"),
                message=n.get("message", ""),
                policy_id=pid or None,
                severity=n.get("severity"),
            )
            for n in notifs
        ]
        outputs.append(
            PolicyOutput(
                policy=p,
                notifications=notifications,
                replacement_opportunity=logic["replacement_opportunity"],
                replacement_reason=logic["replacement_reason"],
                data_quality_issues=logic["data_quality_issues"],
                data_quality_severity=logic["data_quality_severity"],
                income_activation_eligible=logic["income_activation_eligible"],
                income_activation_reason=logic["income_activation_reason"],
                schedule_meeting=logic["schedule_meeting"],
                schedule_meeting_reason=logic["schedule_meeting_reason"],
            )
        )

    out = BookOfBusinessOutput(customer_identifier=customer_identifier, policies=outputs)
    return out.model_dump_json(indent=2, exclude_none=True)


@tool
def get_book_of_business_json_schema() -> str:
    """
    Return the JSON schema for the book-of-business output (customer_identifier + policies with notifications and flags).

    Use this when the user asks for a schema to share with their database admin team to build tables.
    Returns a JSON Schema (draft-07 style) that describes BookOfBusinessOutput and nested types (PolicyOutput, PolicyNotification).
    """
    schema = BookOfBusinessOutput.model_json_schema(mode="serialization")
    return json.dumps(schema, indent=2)


# ---------------------------------------------------------------------------
# System prompt and agent
# ---------------------------------------------------------------------------

BOOK_OF_BUSINESS_SYSTEM_PROMPT = """You are an assistant that scans Sureify APIs and produces the book of business for a given customer.

Your task is to produce the book of business for **Marty McFly** (or the customer identifier you are given):

1. **Scan Sureify APIs** for that customer's book of business using the tools provided.
2. **List all policies** in JSON. The policy shape should be the one returned by the tools (aligned with sureify_models for the frontend).
3. **Include notifications** applicable to each policy (from the tools).
4. **Apply business logic** (already computed by the tools):
   - **Replacements:** Policies where a replacement opportunity exists are marked with replacement_opportunity and replacement_reason.
   - **Data quality:** Policies with missing/invalid data have data_quality_issues and optional data_quality_severity.
   - **Income activation:** Policies eligible for income activation have income_activation_eligible and income_activation_reason.
5. **Scheduled meeting:** Policies that should have a scheduled meeting with the customer are marked with schedule_meeting and schedule_meeting_reason (e.g. replacement opportunity, data quality fix, or income activation).

**Recommended approach:** Use the tool `get_book_of_business_with_notifications_and_flags` with customer_identifier "Marty McFly" to obtain the complete JSON in one call. Then present that JSON to the user (or a summary plus the JSON).

Output format: Provide the full JSON object with key "customer_identifier" and "policies" array. Each policy in "policies" must include the raw policy fields plus: notifications, replacement_opportunity, replacement_reason, data_quality_issues, data_quality_severity, income_activation_eligible, income_activation_reason, schedule_meeting, schedule_meeting_reason. The frontend will consume this JSON as-is.

When the user asks for a JSON schema to share with their database admin team (to build tables), call get_book_of_business_json_schema and provide that schema in your response so they can use it for table design.
"""


def create_agent() -> Agent:
    """Create the Strands agent with book-of-business tools and system prompt."""
    return Agent(
        tools=[
            get_book_of_business,
            get_notifications_for_policies,
            get_book_of_business_with_notifications_and_flags,
            get_book_of_business_json_schema,
        ],
        system_prompt=BOOK_OF_BUSINESS_SYSTEM_PROMPT,
    )


def main() -> None:
    import os
    # If SUREIFY_AGENT_SCHEMA_ONLY=1, print JSON schema for DB team and exit (no LLM)
    if os.environ.get("SUREIFY_AGENT_SCHEMA_ONLY"):
        print(get_book_of_business_json_schema())
        return
    # If SUREIFY_AGENT_TOOL_ONLY=1, skip LLM and just run the composite tool (no Bedrock/credentials needed)
    if os.environ.get("SUREIFY_AGENT_TOOL_ONLY"):
        json_out = get_book_of_business_with_notifications_and_flags("Marty McFly")
        print(json_out)
        return
    agent = create_agent()
    user_message = "Produce the book of business for Marty McFly. List all policies as JSON with notifications and which ones should have a scheduled meeting with the customer."
    result = agent(user_message)
    print(result.get("output", result) if isinstance(result, dict) else result)
>>>>>>> 0cdd862 (agentbuild)


if __name__ == "__main__":
    main()
