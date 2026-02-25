"""
Unified responsible-AI event shape for all agents. Each agent emits AgentRunEvent
so the admin dashboard can show runs, explainability, validation, and guardrail metrics.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentId(str, Enum):
    agent_one = "agent_one"
    agent_two = "agent_two"
    agent_three = "agent_three"


class AgentRunEvent(BaseModel):
    """Single event emitted per agent run for responsible-AI audit and dashboard."""
    event_id: str = Field(..., description="UUID for this event")
    timestamp: str = Field(..., description="ISO 8601 UTC")
    agent_id: AgentId = Field(...)
    run_id: str | None = Field(None, description="Optional; e.g. agentTwo's run_id")
    client_id_scope: str | None = Field(None, description="Redacted/hashed client scope; no PII")
    input_summary: dict[str, Any] = Field(default_factory=dict)
    success: bool = Field(...)
    error_message: str | None = None
    explanation_summary: str | None = None
    data_sources_used: list[str] | None = None
    choice_criteria: list[str] | None = None
    input_validation_passed: bool | None = None
    guardrail_triggered: bool | None = None
    payload_ref: str | None = Field(None, description="FK to agent_two_recommendation_runs.id for drill-down")
