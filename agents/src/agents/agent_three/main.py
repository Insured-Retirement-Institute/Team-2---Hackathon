"""
AgentThree: chatbot that uses the user's current screen state (dashboard, product comparison,
or elsewhere) as context.

**Sureify / API:** AgentThree does not call Sureify or the API directly. All product data,
opportunities, and explainability come from **agentTwo** (the domain agent for product
comparisons and opportunity explainability). AgentTwo uses httpx to call the API server's
passthrough endpoints, so AgentThree always gets up-to-date product and opportunity data
via agentTwo.

**Product comparisons & explainability:** When the user asks about opportunities, "why did
you show me this?", or product comparisons, AgentThree must call the agentTwo tools
(get_recommendation_context, get_product_recommendations_and_explanation) and then explain
the results in a friendly way. It must not answer those questions from its own knowledge.

Run from repo root: PYTHONPATH=. uv run python -m agents.agent_three
"""

from __future__ import annotations

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

from agents.agent_three_schemas import ChatRequest, ChatResponse, ConversationTurn, ScreenState
from agents.agent_two import generate_product_recommendations, get_current_database_context
from agents.audit_writer import persist_event
from agents.responsible_ai_schemas import AgentId, AgentRunEvent


@tool
def get_recommendation_context(client_id: str = "Marty McFly") -> str:
    """
    Get current context for opportunities: DB + Sureify (clients, suitability profiles,
    contracts, products, policies, notifications). Call this when the user asks about
    their data, current products, or context before opportunities.
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
    Get product opportunities and the explanation of why those products were chosen.
    Call this when the user asks for opportunities, "why did you show me this",
    or explainability of opportunities. Pass the changes JSON from the front-end
    (suitability, clientGoals, clientProfile) if available; use "{}" if the user
    just wants an explanation of how opportunities work.
    changes_json: JSON with optional keys "suitability", "clientGoals", "clientProfile".
    client_id: client identifier.
    alert_id: optional IRI alert ID when on product comparison / action flow.
    Returns JSON with opportunities, explanation (summary, data_sources_used, choice_criteria), and storable_payload for the database.
    """
    return generate_product_recommendations(changes_json, client_id, alert_id)


AGENT_THREE_SYSTEM_PROMPT = """You are a helpful chatbot for an insurance/annuity advisory app. The user is talking to you in the context of their current screen. Use the word **opportunity** (or **opportunities**), not "recommendation(s)", when speaking to the user.

**Screen context:** At the start of each turn you will be told where the user is: **dashboard**, **product_comparison**, or **elsewhere**. Use this to tailor your tone and focus:
- On **dashboard**: they may be looking at alerts, policies, or high-level summary. Keep answers relevant to that view.
- On **product_comparison**: they are comparing products or looking at opportunities. They may ask "why did you show me this?" or "explain this product." You MUST use the agentTwo tools to get opportunities and the explanation (summary, criteria, match reasons) and then explain in a friendly, concise way. Do not answer product-comparison or opportunity-explainability questions from your own knowledge.
- **Elsewhere**: general chat; still help with products or opportunities if they ask.

**Product comparisons and explainability are handled by agentTwo (domain agent).** You must always call agentTwo tools for:
- **Products** (opportunities, product list, what products fit)
- **Explainability** ("why did you show me this?", "why this product?", "how did you choose these?")
Do not invent or guess opportunities or reasons—always call:
1. `get_recommendation_context(client_id)` — when they ask what data you have or what context you use (policies, products, suitability from DB + Sureify).
2. `get_product_recommendations_and_explanation(changes_json, client_id, alert_id)` — when they ask for opportunities or explainability. Pass the changes JSON from the message if provided; otherwise "{}". Pass the alert_id from the message if provided (e.g. when on product_comparison screen). Then summarize the returned explanation in plain language (e.g. "We used your risk tolerance and time horizon to pick these products; here's why each one fits...").

**Where the customer is in the experience:** You may be told a more specific location (e.g. viewing a particular alert, on a suitability step, comparing products). Use that to tailor your answer—reference what they're looking at when relevant.

**Reply style:** Be concise and friendly. When you use agentTwo, don't dump raw JSON; summarize the opportunities and the explanation so the user understands why those products were chosen. If there is a storable_payload in the result, you can mention that the explanation has been saved for their records. In a multi-turn conversation, keep context of what was already said and avoid repeating yourself.
"""


def create_agent_three() -> Agent:
    """Create the Strands chatbot agent with screen context and agentTwo delegation tools."""
    logger.debug("Creating agent_three Strands agent with Bedrock")
    return Agent(
        tools=[get_recommendation_context, get_product_recommendations_and_explanation],
        system_prompt=AGENT_THREE_SYSTEM_PROMPT,
    )


def build_user_message_for_agent(
    screen_state: ScreenState,
    user_message: str,
    client_id: str,
    changes_json: str | None,
    alert_id: str = "",
    location_in_experience: str | None = None,
) -> str:
    """Build the message the agent sees: screen context + location in experience + user message + optional changes/alert hint."""
    parts = [
        f"Current screen: **{screen_state.value}**.",
        f"Client: {client_id}.",
        "",
        f"User: {user_message}",
    ]
    if location_in_experience and location_in_experience.strip():
        parts.insert(
            2,
            f"Location in experience: {location_in_experience.strip()} (use this to tailor your answer to what the customer is looking at).",
        )
    if changes_json and changes_json.strip() and changes_json != "{}":
        parts.extend([
            "",
            "Available changes JSON from the front-end (use with get_product_recommendations_and_explanation if the user wants opportunities):",
            changes_json[:2000] + ("..." if len(changes_json) > 2000 else ""),
        ])
    if alert_id and alert_id.strip():
        parts.extend([
            "",
            f"Current alert_id (pass to get_product_recommendations_and_explanation when getting opportunities or explainability): {alert_id.strip()}.",
        ])
    return "\n".join(parts)


def _format_conversation_history_as_string(
    history: list[ConversationTurn] | list[tuple[str, str]],
) -> str:
    """Format conversation history as a single string for the agent. Avoids passing Message
    lists to the model, which can produce content blocks (e.g. markdown) that Bedrock does
    not support (TypeError: content_type=<B> | unsupported type).
    """
    lines: list[str] = ["Previous conversation:", ""]
    for turn in history:
        if isinstance(turn, tuple):
            role, content = turn[0], turn[1]
        else:
            role = turn.role
            content = turn.content
        prefix = "User" if role == "user" else "Assistant"
        lines.append(f"{prefix}: {content}")
        lines.append("")
    lines.append("(Current turn below.)")
    lines.append("")
    return "\n".join(lines)


def run_chat(
    screen_state: ScreenState | str,
    user_message: str,
    client_id: str = "Marty McFly",
    changes_json: str | None = None,
    alert_id: str = "",
    location_in_experience: str | None = None,
    conversation_history: list[ConversationTurn] | list[tuple[str, str]] | None = None,
) -> ChatResponse:
    """
    Run the chatbot with the given screen state and user message. Uses conversation
    history when provided for multi-turn context. Returns a ChatResponse with the reply
    and optional agentTwo summary/storable_payload if we can detect them.
    """
    logger.info("run_chat: screen=%s client_id=%s message_len=%d", screen_state, client_id, len(user_message) if user_message else 0)
    if isinstance(screen_state, str):
        try:
            screen_state = ScreenState(screen_state)
        except ValueError:
            logger.warning("run_chat: invalid screen_state '%s', defaulting to elsewhere", screen_state)
            screen_state = ScreenState.elsewhere
    run_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    input_summary = {
        "screen_state": screen_state.value,
        "client_id_scope": client_id,
        "agent_two_invoked": False,
    }
    try:
        current_turn = build_user_message_for_agent(
            screen_state, user_message, client_id, changes_json, alert_id, location_in_experience
        )
        agent = create_agent_three()
        if conversation_history:
            history_blob = _format_conversation_history_as_string(conversation_history)
            full_message = history_blob + "\n" + current_turn
            result = agent(full_message)
        else:
            result = agent(current_turn)
        reply = result.get("output", result) if isinstance(result, dict) else str(result)
        persist_event(
            AgentRunEvent(
                event_id=str(uuid.uuid4()),
                timestamp=timestamp,
                agent_id=AgentId.agent_three,
                run_id=run_id,
                client_id_scope=client_id,
                input_summary=input_summary,
                success=True,
                explanation_summary="Chat reply generated",
                input_validation_passed=True,
                guardrail_triggered=None,
            )
        )
        return ChatResponse(
            reply=reply,
            screen_state=screen_state,
            agent_two_invoked=False,
            agent_two_summary=None,
            storable_payload=None,
        )
    except Exception as e:
        logger.exception("run_chat failed: screen=%s client_id=%s", screen_state.value if hasattr(screen_state, "value") else screen_state, client_id)
        persist_event(
            AgentRunEvent(
                event_id=str(uuid.uuid4()),
                timestamp=timestamp,
                agent_id=AgentId.agent_three,
                run_id=run_id,
                client_id_scope=client_id,
                input_summary=input_summary,
                success=False,
                error_message=str(e),
                input_validation_passed=True,
                guardrail_triggered=None,
            )
        )
        raise


def run_interactive(
    screen_state: ScreenState | str = "elsewhere",
    client_id: str = "Marty McFly",
    changes_json: str | None = None,
    alert_id: str = "",
    location_in_experience: str | None = None,
) -> None:
    """
    Run an interactive conversation with agent three. Reads user input from stdin
    and prints replies; conversation history is kept for context. Type 'quit' or
    'exit' to end.
    """
    if isinstance(screen_state, str):
        try:
            screen_state = ScreenState(screen_state)
        except ValueError:
            screen_state = ScreenState.elsewhere
    history: list[tuple[str, str]] = []
    print(
        f"AgentThree conversation (screen={screen_state.value}, client={client_id}). "
        "Ask about products, opportunities, or explainability. Type 'quit' or 'exit' to end.\n"
    )
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break
        response = run_chat(
            screen_state=screen_state,
            user_message=user_input,
            client_id=client_id,
            changes_json=changes_json,
            alert_id=alert_id,
            location_in_experience=location_in_experience,
            conversation_history=history if history else None,
        )
        print(f"\nAssistant: {response.reply}\n")
        history.append((user_input, response.reply))


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="AgentThree: chatbot with screen context; delegates to agentTwo for products/explainability")
    parser.add_argument("--screen", type=str, default="elsewhere", choices=["dashboard", "product_comparison", "elsewhere"], help="Current screen state")
    parser.add_argument("--message", type=str, help="User message (omit for interactive mode with --interactive)")
    parser.add_argument("--interactive", action="store_true", help="Run an interactive conversation (read messages from stdin)")
    parser.add_argument("--client-id", type=str, default="Marty McFly", help="Client identifier for agentTwo")
    parser.add_argument("--changes", type=str, help="Path to JSON file with suitability/clientGoals/clientProfile (optional)")
    parser.add_argument("--alert-id", type=str, default="", help="Optional IRI alert ID")
    parser.add_argument("--location", type=str, default="", dest="location_in_experience", help="Where the customer is in the experience (e.g. viewing_alert_123)")
    args = parser.parse_args()

    changes_json = None
    if args.changes:
        p = Path(args.changes)
        if p.exists():
            changes_json = p.read_text()

    location = (args.location_in_experience or "").strip() or None

    if args.interactive or (args.message is None and sys.stdin.isatty()):
        run_interactive(
            screen_state=args.screen,
            client_id=args.client_id,
            changes_json=changes_json,
            alert_id=args.alert_id,
            location_in_experience=location,
        )
        return

    message = args.message or "What can you help me with?"
    response = run_chat(
        screen_state=args.screen,
        user_message=message,
        client_id=args.client_id,
        changes_json=changes_json,
        alert_id=args.alert_id,
        location_in_experience=location,
    )
    print(response.reply)


if __name__ == "__main__":
    main()
