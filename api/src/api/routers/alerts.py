"""
IRI API endpoints for alerts and dashboard.
Implements the IRI Annuity Renewal Intelligence API spec.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.database import fetch_rows, pool
from schemas.iri_schemas import (
    RenewalAlert,
    DashboardStats,
    Priority,
    Status,
)

router = APIRouter(prefix="/api", tags=["IRI Dashboard"])


# Request/Response models
class SnoozeRequest(BaseModel):
    snoozeDays: int
    reason: str | None = None


class DismissRequest(BaseModel):
    reason: str


class ApiResponse(BaseModel):
    success: bool
    message: str
    snoozeUntil: str | None = None


class AlertDetail(BaseModel):
    """Full alert detail with policy data, suitability, disclosures, etc."""
    alert: RenewalAlert
    clientAlerts: list[RenewalAlert] | None = None
    policyData: dict | None = None
    aiSuitabilityScore: dict | None = None
    suitabilityData: dict | None = None
    disclosureItems: list[dict] | None = None
    transactionOptions: list[dict] | None = None
    auditLog: list[dict] | None = None


# Agent One output models
class PolicyOutput(BaseModel):
    """PolicyOutput from agent_one (matches agentOneOutputSchema.json)"""
    policy: dict  # Full policy object
    notifications: list[dict] = []
    replacement_opportunity: bool = False
    replacement_reason: str | None = None
    data_quality_issues: list[str] = []
    data_quality_severity: str | None = None
    income_activation_eligible: bool = False
    income_activation_reason: str | None = None
    schedule_meeting: bool = False
    schedule_meeting_reason: str | None = None


class BookOfBusinessOutput(BaseModel):
    """BookOfBusinessOutput from agent_one (matches agentOneOutputSchema.json)"""
    customer_identifier: str
    policies: list[PolicyOutput]


@router.get("/alerts", response_model=list[RenewalAlert])
async def get_alerts(
    status: Annotated[Status | None, Query()] = None,
    priority: Annotated[Priority | None, Query()] = None,
    carrier: Annotated[str | None, Query()] = None,
) -> list[RenewalAlert]:
    """
    Get all renewal alerts with optional filtering.

    The UI calls this endpoint to display the list of alerts on the dashboard.
    """
    # Convert enums to strings for SQL query
    status_str = status.value if status else None
    priority_str = priority.value if priority else None

    rows = await fetch_rows("get_alerts", status_str, priority_str, carrier)

    # Convert database rows to Pydantic models
    alerts = []
    for row in rows:
        # Handle array fields properly
        alert_data = dict(row)
        if alert_data.get("alertTypes"):
            alert_data["alertTypes"] = [alert_data["alertTypes"]]
        alerts.append(RenewalAlert(**alert_data))

    return alerts


@router.post("/alerts")
async def create_alerts(book_of_business: BookOfBusinessOutput):
    """
    Create alerts from agent_one BookOfBusinessOutput.

    Accepts the complete output from agent_one and creates one alert per policy
    in the alerts table. Each alert stores:
    - Flat columns extracted from the policy for querying (policy_id, carrier, etc.)
    - Full PolicyOutput object in alert_detail JSONB column
    - Full BookOfBusinessOutput in agent_data JSONB column
    """
    if not book_of_business.policies:
        return {"success": True, "message": "No policies to process", "created": 0}

    created_count = 0
    errors = []

    for policy_output in book_of_business.policies:
        try:
            policy = policy_output.policy

            # Extract flat fields from policy
            policy_id = policy.get("contractId") or policy.get("ID", "unknown")
            client_name = policy.get("clientName", "Unknown Client")
            carrier = policy.get("carrier", "Unknown Carrier")
            renewal_date = policy.get("renewalDate", "Unknown")
            current_rate = policy.get("currentRate", "Unknown")
            renewal_rate = policy.get("renewalRate", "Unknown")
            current_value = policy.get("currentValue", "$0")
            is_min_rate = policy.get("isMinRateRenewal", False)

            # Calculate days until renewal (default to 365 if not available)
            days_until_renewal = 365  # Default
            try:
                if renewal_date and renewal_date != "Unknown":
                    # Try to parse renewal_date if it's a date string
                    # For now, use a default value
                    pass
            except Exception:
                pass

            # Determine priority based on days until renewal and flags
            if days_until_renewal < 30 or policy_output.replacement_opportunity:
                priority = "high"
            elif days_until_renewal < 90 or policy_output.data_quality_issues:
                priority = "medium"
            else:
                priority = "low"

            # Determine primary alert_type
            if policy_output.replacement_opportunity:
                alert_type = "replacement_opportunity"
            elif policy_output.data_quality_issues:
                alert_type = "missing_info"
            elif policy_output.income_activation_eligible:
                alert_type = "income_planning"
            elif policy_output.schedule_meeting:
                alert_type = "suitability_review"
            else:
                alert_type = "replacement_opportunity"  # Default

            # Build alert_types array
            alert_types = []
            if policy_output.replacement_opportunity:
                alert_types.append("replacement_opportunity")
            if policy_output.data_quality_issues:
                alert_types.append("missing_info")
            if policy_output.income_activation_eligible:
                alert_types.append("income_planning")
            if policy_output.schedule_meeting:
                alert_types.append("suitability_review")

            # Build alert description
            alert_description = ""
            if policy_output.replacement_opportunity and policy_output.replacement_reason:
                alert_description = policy_output.replacement_reason
            elif policy_output.data_quality_issues:
                alert_description = f"Data quality issues: {', '.join(policy_output.data_quality_issues[:3])}"
            elif policy_output.income_activation_reason:
                alert_description = policy_output.income_activation_reason
            elif policy_output.schedule_meeting_reason:
                alert_description = policy_output.schedule_meeting_reason
            else:
                alert_description = f"Renewal alert for policy {policy_id}"

            # Generate alert ID
            alert_id = f"alert-{policy_id}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

            # Determine has_data_exception
            has_data_exception = bool(policy_output.data_quality_issues)

            # Extract missing_fields from data_quality_issues
            missing_fields = policy_output.data_quality_issues if policy_output.data_quality_issues else None

            # Insert or update alert
            await pool.execute(
                """
                INSERT INTO alerts (
                    id,
                    customer_identifier,
                    policy_id,
                    client_name,
                    carrier,
                    renewal_date,
                    days_until_renewal,
                    current_rate,
                    renewal_rate,
                    current_value,
                    is_min_rate,
                    priority,
                    has_data_exception,
                    missing_fields,
                    status,
                    alert_type,
                    alert_types,
                    alert_description,
                    alert_detail,
                    agent_data,
                    created_at,
                    updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22)
                ON CONFLICT (id) DO UPDATE SET
                    customer_identifier = EXCLUDED.customer_identifier,
                    client_name = EXCLUDED.client_name,
                    carrier = EXCLUDED.carrier,
                    renewal_date = EXCLUDED.renewal_date,
                    days_until_renewal = EXCLUDED.days_until_renewal,
                    current_rate = EXCLUDED.current_rate,
                    renewal_rate = EXCLUDED.renewal_rate,
                    current_value = EXCLUDED.current_value,
                    is_min_rate = EXCLUDED.is_min_rate,
                    priority = EXCLUDED.priority,
                    has_data_exception = EXCLUDED.has_data_exception,
                    missing_fields = EXCLUDED.missing_fields,
                    alert_type = EXCLUDED.alert_type,
                    alert_types = EXCLUDED.alert_types,
                    alert_description = EXCLUDED.alert_description,
                    alert_detail = EXCLUDED.alert_detail,
                    agent_data = EXCLUDED.agent_data,
                    updated_at = EXCLUDED.updated_at
                """,
                alert_id,
                book_of_business.customer_identifier,
                policy_id,
                client_name,
                carrier,
                renewal_date,
                days_until_renewal,
                current_rate,
                renewal_rate,
                current_value,
                is_min_rate,
                priority,
                has_data_exception,
                missing_fields,
                "pending",  # Default status
                alert_type,
                alert_types,
                alert_description,
                json.dumps(policy_output.model_dump()),  # Store full PolicyOutput
                json.dumps(book_of_business.model_dump()),  # Store full BookOfBusinessOutput
                datetime.now(timezone.utc),
                datetime.now(timezone.utc)
            )

            created_count += 1

        except Exception as e:
            errors.append(f"Error processing policy {policy.get('contractId', 'unknown')}: {str(e)}")
            continue

    if errors:
        return {
            "success": True,
            "message": f"Created {created_count} alerts with {len(errors)} errors",
            "created": created_count,
            "errors": errors
        }

    return {
        "success": True,
        "message": f"Successfully created {created_count} alerts",
        "created": created_count
    }


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats() -> DashboardStats:
    """
    Get dashboard statistics summary.

    The UI calls this to display high-level metrics at the top of the dashboard.
    """
    rows = await fetch_rows("get_dashboard_stats")

    if not rows:
        return DashboardStats(total=0, high=0, urgent=0, totalValue=0.0)

    return DashboardStats(**rows[0])


@router.get("/alerts/{alert_id}", response_model=AlertDetail)
async def get_alert_detail(alert_id: str) -> AlertDetail:
    """
    Get detailed information about a specific alert.

    Returns AlertDetail with alert info, policy data, suitability, disclosures, etc.
    The UI calls this when a user clicks on an alert to view full details.
    """
    rows = await fetch_rows("get_alert_by_id", alert_id)

    if not rows:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert_row = dict(rows[0])

    # Build RenewalAlert from row data
    renewal_alert = RenewalAlert(**{
        k: v for k, v in alert_row.items()
        if k not in ['alert_detail', 'agent_data']
    })

    # If alert_detail JSON exists, use it for full detail
    if alert_row.get("alert_detail"):
        detail_json = alert_row["alert_detail"]
        # Return AlertDetail with data from alert_detail JSONB
        return AlertDetail(
            alert=renewal_alert,
            clientAlerts=detail_json.get("clientAlerts"),
            policyData=detail_json.get("policyData"),
            aiSuitabilityScore=detail_json.get("aiSuitabilityScore"),
            suitabilityData=detail_json.get("suitabilityData"),
            disclosureItems=detail_json.get("disclosureItems"),
            transactionOptions=detail_json.get("transactionOptions"),
            auditLog=detail_json.get("auditLog"),
        )

    # Otherwise return basic AlertDetail with just the alert
    return AlertDetail(
        alert=renewal_alert,
        clientAlerts=[],
        policyData=None,
        aiSuitabilityScore=None,
        suitabilityData=None,
        disclosureItems=[],
        transactionOptions=[],
        auditLog=[],
    )


@router.post("/alerts/{alert_id}/snooze", response_model=ApiResponse)
async def snooze_alert(alert_id: str, request: SnoozeRequest) -> ApiResponse:
    """
    Snooze an alert for a specified number of days.

    The UI calls this when a user clicks the snooze button on an alert.
    """
    if request.snoozeDays < 1 or request.snoozeDays > 90:
        raise HTTPException(
            status_code=400,
            detail="snoozeDays must be between 1 and 90"
        )

    rows = await fetch_rows("snooze_alert", alert_id, request.snoozeDays)

    if not rows:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    snooze_until = rows[0]["snoozed_until"].isoformat() if rows[0].get("snoozed_until") else None

    return ApiResponse(
        success=True,
        message=f"Alert snoozed for {request.snoozeDays} days",
        snoozeUntil=snooze_until
    )


@router.post("/alerts/{alert_id}/dismiss", response_model=ApiResponse)
async def dismiss_alert(alert_id: str, request: DismissRequest) -> ApiResponse:
    """
    Dismiss an alert permanently.

    The UI calls this when a user dismisses an alert.
    """
    if not request.reason:
        raise HTTPException(status_code=400, detail="reason is required")

    rows = await fetch_rows("dismiss_alert", alert_id)

    if not rows:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    return ApiResponse(
        success=True,
        message="Alert dismissed successfully"
    )


class SuitabilityData(BaseModel):
    """Client suitability assessment data"""
    clientObjectives: str
    riskTolerance: str
    timeHorizon: str
    liquidityNeeds: str
    taxConsiderations: str
    guaranteedIncome: str
    rateExpectations: str
    surrenderTimeline: str
    livingBenefits: list[str]
    advisorEligibility: str
    score: int
    isPrefilled: bool


@router.put("/alerts/{alert_id}/suitability")
async def save_suitability(
    alert_id: str,
    suitability: SuitabilityData
):
    """
    Save suitability data for an alert.

    Logic:
    1. Lookup alert_detail from alerts table using alert_id
    2. Extract clientId from alert_detail.policy.clientId
    3. Use that clientId to update client_suitability_data table
    4. Requires client_profiles record to exist first (FK constraint)
    """
    # 1. Get alert_detail from alerts table
    alert_row = await pool.fetchrow(
        "SELECT alert_detail FROM alerts WHERE id = $1",
        alert_id
    )

    if not alert_row:
        raise HTTPException(
            status_code=404,
            detail=f"Alert {alert_id} not found"
        )

    # 2. Extract clientId from alert_detail.policy.clientId
    alert_detail = alert_row.get('alert_detail')
    if not alert_detail:
        raise HTTPException(
            status_code=400,
            detail=f"Alert {alert_id} has no alert_detail data"
        )

    policy_data = alert_detail.get('policy', {})
    client_id = policy_data.get('clientId')

    if not client_id:
        raise HTTPException(
            status_code=400,
            detail=f"Alert {alert_id} has no clientId in policy data"
        )

    # 3. Verify client_profiles record exists (FK constraint requirement)
    profile_exists = await pool.fetchrow(
        "SELECT client_id FROM client_profiles WHERE client_id = $1",
        client_id
    )

    if not profile_exists:
        raise HTTPException(
            status_code=400,
            detail=f"Client profile must be fetched at least once before saving suitability data. Client ID: {client_id}"
        )

    # 4. Insert or update suitability data
    await pool.execute(
        """
        INSERT INTO client_suitability_data (
            client_id,
            client_objectives,
            risk_tolerance,
            time_horizon,
            liquidity_needs,
            tax_considerations,
            guaranteed_income,
            rate_expectations,
            surrender_timeline,
            living_benefits,
            advisor_eligibility,
            score,
            is_prefilled,
            updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, now())
        ON CONFLICT (client_id) DO UPDATE SET
            client_objectives = EXCLUDED.client_objectives,
            risk_tolerance = EXCLUDED.risk_tolerance,
            time_horizon = EXCLUDED.time_horizon,
            liquidity_needs = EXCLUDED.liquidity_needs,
            tax_considerations = EXCLUDED.tax_considerations,
            guaranteed_income = EXCLUDED.guaranteed_income,
            rate_expectations = EXCLUDED.rate_expectations,
            surrender_timeline = EXCLUDED.surrender_timeline,
            living_benefits = EXCLUDED.living_benefits,
            advisor_eligibility = EXCLUDED.advisor_eligibility,
            score = EXCLUDED.score,
            is_prefilled = EXCLUDED.is_prefilled,
            updated_at = now()
        """,
        client_id,
        suitability.clientObjectives,
        suitability.riskTolerance,
        suitability.timeHorizon,
        suitability.liquidityNeeds,
        suitability.taxConsiderations,
        suitability.guaranteedIncome,
        suitability.rateExpectations,
        suitability.surrenderTimeline,
        suitability.livingBenefits,
        suitability.advisorEligibility,
        suitability.score,
        suitability.isPrefilled
    )

    return {"success": True, "message": "Suitability data saved"}
