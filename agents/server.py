"""
FastAPI HTTP wrapper for all agents. Provides HTTP endpoints for invoking agents
and health checks for Kubernetes probes.

Run locally: uvicorn agents.server:app --reload --port 8000
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

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

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Agents API",
    description="HTTP wrapper for agent_one, agent_two, and agent_three",
    version="0.1.0",
)


class HealthResponse(BaseModel):
    status: str
    service: str


class AgentOneRequest(BaseModel):
    customer_identifier: str = "Marty McFly"
    format: str = "book_of_business"  # "book_of_business" or "iri_alerts"
    use_llm: bool = False
    message: str | None = None


class AgentOneResponse(BaseModel):
    result: Any
    format: str


class CreateAlertsRequest(BaseModel):
    customer_identifier: str = "Marty McFly"


class CreateAlertsResponse(BaseModel):
    success: bool
    message: str
    created: int
    errors: list[str] | None = None


class AgentTwoContextRequest(BaseModel):
    client_id: str = "Marty McFly"


class AgentTwoRecommendationsRequest(BaseModel):
    client_id: str = "Marty McFly"
    changes_json: str = "{}"
    alert_id: str = ""
    use_llm: bool = False
    message: str | None = None


class AgentTwoResponse(BaseModel):
    result: Any


class AgentThreeChatRequest(BaseModel):
    screen: str = "dashboard"  # "dashboard", "product_comparison", "elsewhere"
    message: str
    client_id: str = "Marty McFly"
    changes_json: str | None = None
    alert_id: str = ""


class AgentThreeChatResponse(BaseModel):
    reply: str
    screen_state: str
    agent_two_invoked: bool
    agent_two_summary: str | None = None
    storable_payload: Any | None = None


@app.get("/health", response_model=HealthResponse)
def health():
    """Liveness probe endpoint."""
    return HealthResponse(status="ok", service="agents")


@app.get("/health/ready", response_model=HealthResponse)
def health_ready():
    """Readiness probe endpoint."""
    return HealthResponse(status="ok", service="agents")


@app.post("/agent-one/book-of-business", response_model=AgentOneResponse)
def agent_one_book_of_business(request: AgentOneRequest):
    """
    Invoke agent_one to get book of business.

    - format="book_of_business": Returns full book with notifications and flags
    - format="iri_alerts": Returns IRI API format (alerts + dashboardStats)
    - use_llm=true: Uses Strands agent with Bedrock LLM
    """
    try:
        from agents.agent_one.main import (
            create_agent,
            get_book_of_business_as_iri_alerts,
            get_book_of_business_with_notifications_and_flags,
        )

        if request.use_llm:
            agent = create_agent()
            message = request.message or f"Produce the book of business for {request.customer_identifier}."
            result = agent(message)
            output = result.get("output", result) if isinstance(result, dict) else str(result)
            return AgentOneResponse(result=output, format="llm_response")

        if request.format == "iri_alerts":
            result = get_book_of_business_as_iri_alerts(request.customer_identifier)
        else:
            result = get_book_of_business_with_notifications_and_flags(request.customer_identifier)

        import json
        return AgentOneResponse(result=json.loads(result), format=request.format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent-one/create-alerts", response_model=CreateAlertsResponse)
def agent_one_create_alerts(request: CreateAlertsRequest):
    """
    Generate book of business and push alerts to IRI API database.

    This endpoint:
    1. Fetches policies from Sureify
    2. Applies business logic (replacements, data quality, etc.)
    3. POSTs the BookOfBusinessOutput to POST /api/alerts
    4. Returns success response with created alert count

    Requires IRI_API_BASE_URL environment variable to be set.
    """
    try:
        from agents.agent_one.main import get_book_of_business_with_notifications_and_flags
        from agents.schemas import BookOfBusinessOutput
        from agents.iri_client import create_iri_alerts

        # Generate book of business
        json_output = get_book_of_business_with_notifications_and_flags(request.customer_identifier)
        book = BookOfBusinessOutput.model_validate_json(json_output)

        # Push to IRI API
        result = create_iri_alerts(book)

        # Check for errors
        if isinstance(result, dict) and result.get("error"):
            raise HTTPException(status_code=500, detail=result.get("message", "Failed to create alerts"))

        # Return success response
        return CreateAlertsResponse(
            success=result.get("success", True),
            message=result.get("message", "Alerts created successfully"),
            created=result.get("created", len(book.policies)),
            errors=result.get("errors")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent-two/context", response_model=AgentTwoResponse)
def agent_two_context(request: AgentTwoContextRequest):
    """Get current database context for a client (DB + Sureify data)."""
    try:
        from agents.agent_two.main import get_current_database_context

        result = get_current_database_context(request.client_id)
        import json
        return AgentTwoResponse(result=json.loads(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent-two/recommendations", response_model=AgentTwoResponse)
def agent_two_recommendations(request: AgentTwoRecommendationsRequest):
    """
    Generate product recommendations based on client profile changes.

    - changes_json: JSON with optional keys "suitability", "clientGoals", "clientProfile"
    - use_llm=true: Uses Strands agent with Bedrock LLM
    """
    try:
        from agents.agent_two.main import create_agent_two, generate_product_recommendations

        if request.use_llm:
            agent = create_agent_two()
            message = request.message or (
                f"Get current database context for client_id '{request.client_id}', "
                f"then generate product recommendations using this changes JSON:\n{request.changes_json}"
            )
            result = agent(message)
            output = result.get("output", result) if isinstance(result, dict) else str(result)
            return AgentTwoResponse(result=output)

        result = generate_product_recommendations(
            request.changes_json,
            request.client_id,
            request.alert_id,
        )
        import json
        return AgentTwoResponse(result=json.loads(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent-three/chat", response_model=AgentThreeChatResponse)
def agent_three_chat(request: AgentThreeChatRequest):
    """
    Chat with agent_three. Always uses LLM (Strands agent with Bedrock).

    - screen: Current UI screen context ("dashboard", "product_comparison", "elsewhere")
    - message: User message to the chatbot
    """
    try:
        from agents.agent_three.main import run_chat

        response = run_chat(
            screen_state=request.screen,
            user_message=request.message,
            client_id=request.client_id,
            changes_json=request.changes_json,
            alert_id=request.alert_id,
        )
        return AgentThreeChatResponse(
            reply=response.reply,
            screen_state=response.screen_state.value if hasattr(response.screen_state, "value") else str(response.screen_state),
            agent_two_invoked=response.agent_two_invoked,
            agent_two_summary=response.agent_two_summary,
            storable_payload=response.storable_payload.model_dump() if response.storable_payload else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
