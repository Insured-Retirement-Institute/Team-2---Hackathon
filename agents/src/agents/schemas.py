"""
Agent output schemas: policy + notifications + business logic flags.

These extend the policy payload (from api.src.api.sureify_models) with
fields for the frontend: notifications, replacement, data quality,
income activation, and scheduled-meeting recommendation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PolicyNotification(BaseModel):
    """A single notification applicable to a policy."""

    notification_type: str = Field(..., description="Type of notification (e.g. premium_due, lapse_risk)")
    message: str = Field(..., description="Short description for the user")
    policy_id: str | None = Field(None, description="Policy ID this notification applies to")
    severity: str | None = Field(None, description="e.g. info, warning, urgent")


class PolicyOutput(BaseModel):
    """
    Policy record with agent-derived fields for the book-of-business dashboard.

    The `policy` field holds the raw policy (dict form of Policy/Annuity/Life from
    sureify_models). The remaining fields are added by the agent/tools layer.
    """

    policy: dict[str, Any] = Field(
        ...,
        description="Policy data (JSON-serializable dict from sureify_models Policy/Annuity/Life)",
    )
    notifications: list[PolicyNotification] = Field(
        default_factory=list,
        description="Notifications applicable to this policy",
    )
    replacement_opportunity: bool = Field(
        False,
        description="True if a replacement opportunity exists for this policy",
    )
    replacement_reason: str | None = Field(
        None,
        description="Short reason for replacement opportunity, if any",
    )
    data_quality_issues: list[str] = Field(
        default_factory=list,
        description="List of data quality issues (e.g. missing SSN, address)",
    )
    data_quality_severity: str | None = Field(
        None,
        description="Overall severity of data quality issues if any",
    )
    income_activation_eligible: bool = Field(
        False,
        description="True if policy is eligible for income activation",
    )
    income_activation_reason: str | None = Field(
        None,
        description="Short reason for income activation eligibility, if any",
    )
    schedule_meeting: bool = Field(
        False,
        description="True if a scheduled meeting with the customer is recommended",
    )
    schedule_meeting_reason: str | None = Field(
        None,
        description="Reason(s) to schedule a meeting (e.g. replacement; data quality; income activation)",
    )


class BookOfBusinessOutput(BaseModel):
    """Full book-of-business response: list of policies with notifications and flags."""

    customer_identifier: str = Field(
        ...,
        description="Customer or advisor identifier (e.g. Marty McFly)",
    )
    policies: list[PolicyOutput] = Field(
        default_factory=list,
        description="All policies with notifications and business-logic flags",
    )
