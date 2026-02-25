"""
Schemas for agentThree (chatbot): screen state context and chat request/response.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ScreenState(str, Enum):
    """Where the user is on the screen. Front-end sends this as context for the chatbot."""
    dashboard = "dashboard"
    product_comparison = "product_comparison"
    elsewhere = "elsewhere"


# ---- Chat request (front-end → agentThree) ----
class ChatRequest(BaseModel):
    """Request to agentThree chatbot. Include screen state and optional client_id for agentTwo calls."""
    screen_state: ScreenState = Field(
        ...,
        description="Current screen: dashboard, product_comparison, or elsewhere",
    )
    user_message: str = Field(..., description="What the user said or asked")
    client_id: str = Field(
        default="Marty McFly",
        description="Client identifier; used when calling agentTwo for context or recommendations",
    )
    changes_json: str | None = Field(
        None,
        description="Optional JSON with suitability/clientGoals/clientProfile; used if user asks for recommendations and front-end has form data",
    )
    alert_id: str = Field(default="", description="Optional IRI alert ID when on product comparison / action flow")


# ---- Chat response (agentThree → front-end) ----
class ChatResponse(BaseModel):
    """Response from agentThree chatbot."""
    reply: str = Field(..., description="The chatbot's reply to the user")
    screen_state: ScreenState = Field(..., description="Echo of the screen state used as context")
    agent_two_invoked: bool = Field(
        default=False,
        description="True if agentThree called agentTwo (context or recommendations)",
    )
    agent_two_summary: str | None = Field(
        None,
        description="Short summary of what agentTwo returned (e.g. '3 recommendations with explanation')",
    )
    storable_payload: dict[str, Any] | None = Field(
        None,
        description="If agentTwo returned recommendations, the storable_payload for the database",
    )
