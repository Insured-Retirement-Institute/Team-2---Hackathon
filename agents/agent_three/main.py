"""
AgentThree: chatbot that uses the user's current screen state (dashboard, product comparison,
or elsewhere) as context. For product-related questions or recommendation explainability,
it delegates to agentTwo and explains the results in a friendly way.

Run from repo root: PYTHONPATH=. uv run python -m agents.agent_three
"""

from __future__ import annotations

import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
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

from agents.agent_three_schemas import ChatRequest, ChatResponse, ScreenState
from agents.agent_two import generate_product_recommendations, get_current_database_context


@tool
def get_recommendation_context(client_id: str = "Marty McFly") -> str:
    """
    Get current context for recommendations: DB + Sureify (clients, suitability profiles,
    contracts, products, policies, notifications). Call this when the user asks about
    their data, current products, or context before recommendations.
    client_id: client identifier (e.g. "Marty McFly").
    """
    return get_current_database_context(client_id)


@tool
def get_product_recommendations_and_explanation(
    changes_json: str,
    client_id: str = "Marty McFly",
    alert_id: str = "",
) -> str:
    """
    Get product recommendations and the explanation of why those products were chosen.
    Call this when the user asks for recommendations, "why did you recommend this",
    or explainability of recommendations. Pass the changes JSON from the front-end
    (suitability, clientGoals, clientProfile) if available; use "{}" if the user
    just wants an explanation of how recommendations work.
    changes_json: JSON with optional keys "suitability", "clientGoals", "clientProfile".
    client_id: client identifier.
    alert_id: optional IRI alert ID when on product comparison / action flow.
    Returns JSON with recommendations, explanation (summary, data_sources_used, choice_criteria), and storable_payload for the database.
    """
    return generate_product_recommendations(changes_json, client_id, alert_id)


AGENT_THREE_SYSTEM_PROMPT = """You are a helpful chatbot for an insurance/annuity advisory app. The user is talking to you in the context of their current screen.

**Screen context:** At the start of each turn you will be told where the user is: **dashboard**, **product_comparison**, or **elsewhere**. Use this to tailor your tone and focus:
- On **dashboard**: they may be looking at alerts, policies, or high-level summary. Keep answers relevant to that view.
- On **product_comparison**: they are comparing products or looking at recommendations. They may ask "why did you recommend this?" or "explain this product." Use the agentTwo tools to get recommendations and the explanation (summary, criteria, match reasons) and explain in a friendly, concise way.
- **Elsewhere**: general chat; still help with products or recommendations if they ask.

**When to call agentTwo:** If the user asks about:
- **Products** (recommendations, product list, what products fit)
- **Explainability** ("why did you recommend this?", "why this product?", "how did you choose these?")
then use the tools:
1. `get_recommendation_context(client_id)` — to get current data (policies, products, suitability) when they ask what you have or what context you use.
2. `get_product_recommendations_and_explanation(changes_json, client_id, alert_id)` — to get recommendations and the structured explanation (summary, data_sources_used, choice_criteria, match_reason per product). If the user or system provided a changes JSON (suitability, client goals, profile), pass it; otherwise pass "{}" to get recommendations based on existing context. Then summarize the explanation in plain language (e.g. "We used your risk tolerance and time horizon to pick these products; here's why each one fits...").

**Reply style:** Be concise and friendly. When you use agentTwo, don't dump raw JSON; summarize the recommendations and the explanation so the user understands why those products were chosen. If there is a storable_payload in the result, you can mention that the explanation has been saved for their records.
"""


def create_agent_three() -> Agent:
    """Create the Strands chatbot agent with screen context and agentTwo delegation tools."""
    return Agent(
        tools=[get_recommendation_context, get_product_recommendations_and_explanation],
        system_prompt=AGENT_THREE_SYSTEM_PROMPT,
    )


def build_user_message_for_agent(screen_state: ScreenState, user_message: str, client_id: str, changes_json: str | None) -> str:
    """Build the message the agent sees: screen context + user message + optional changes hint."""
    parts = [
        f"Current screen: **{screen_state.value}**.",
        f"Client: {client_id}.",
        "",
        f"User: {user_message}",
    ]
    if changes_json and changes_json.strip() and changes_json != "{}":
        parts.extend([
            "",
            "Available changes JSON from the front-end (use with get_product_recommendations_and_explanation if the user wants recommendations):",
            changes_json[:2000] + ("..." if len(changes_json) > 2000 else ""),
        ])
    return "\n".join(parts)


def run_chat(
    screen_state: ScreenState | str,
    user_message: str,
    client_id: str = "Marty McFly",
    changes_json: str | None = None,
    alert_id: str = "",
) -> ChatResponse:
    """
    Run the chatbot with the given screen state and user message. Returns a ChatResponse
    with the reply and optional agentTwo summary/storable_payload if we can detect them.
    """
    if isinstance(screen_state, str):
        try:
            screen_state = ScreenState(screen_state)
        except ValueError:
            screen_state = ScreenState.elsewhere
    message = build_user_message_for_agent(screen_state, user_message, client_id, changes_json)
    agent = create_agent_three()
    result = agent(message)
    reply = result.get("output", result) if isinstance(result, dict) else str(result)
    return ChatResponse(
        reply=reply,
        screen_state=screen_state,
        agent_two_invoked=False,
        agent_two_summary=None,
        storable_payload=None,
    )


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="AgentThree: chatbot with screen context; delegates to agentTwo for products/explainability")
    parser.add_argument("--screen", type=str, default="elsewhere", choices=["dashboard", "product_comparison", "elsewhere"], help="Current screen state")
    parser.add_argument("--message", type=str, default="What can you help me with?", help="User message")
    parser.add_argument("--client-id", type=str, default="Marty McFly", help="Client identifier for agentTwo")
    parser.add_argument("--changes", type=str, help="Path to JSON file with suitability/clientGoals/clientProfile (optional)")
    parser.add_argument("--alert-id", type=str, default="", help="Optional IRI alert ID")
    args = parser.parse_args()

    changes_json = None
    if args.changes:
        p = Path(args.changes)
        if p.exists():
            changes_json = p.read_text()

    response = run_chat(
        screen_state=args.screen,
        user_message=args.message,
        client_id=args.client_id,
        changes_json=changes_json,
        alert_id=args.alert_id,
    )
    print(response.reply)


if __name__ == "__main__":
    main()
