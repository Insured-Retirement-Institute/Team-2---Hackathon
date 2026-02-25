"""
IRI API endpoints for alerts and dashboard.
Implements the IRI Annuity Renewal Intelligence API spec.
"""
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
