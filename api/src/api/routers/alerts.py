"""
IRI API endpoints for alerts and dashboard.
Implements the IRI Annuity Renewal Intelligence API spec.
"""
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.database import fetch_rows, pool

# Import generated Pydantic models from agents package
import sys
from pathlib import Path
agents_dir = Path(__file__).parent.parent.parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

from iri_schemas import (
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


@router.get("/alerts/{alert_id}")
async def get_alert_detail(alert_id: str):
    """
    Get detailed information about a specific alert.

    The UI calls this when a user clicks on an alert to view full details.
    """
    rows = await fetch_rows("get_alert_by_id", alert_id)

    if not rows:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert = dict(rows[0])

    # If alert_detail JSON exists, merge it into the response
    if alert.get("alert_detail"):
        detail_json = alert.pop("alert_detail")
        # The alert_detail column contains the full AlertDetail structure
        return detail_json

    # Otherwise return basic alert info
    return RenewalAlert(**alert)


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
    1. Lookup customer_identifier from alerts table using alert_id
    2. Use that as clientId to update client_suitability_data table
    3. Requires client_profiles record to exist first (FK constraint)
    """
    # 1. Get customer_identifier from alerts table
    alert_row = await pool.fetchrow(
        "SELECT customer_identifier FROM alerts WHERE id = $1",
        alert_id
    )

    if not alert_row or not alert_row['customer_identifier']:
        raise HTTPException(
            status_code=404,
            detail=f"Alert {alert_id} not found or has no customer_identifier"
        )

    client_id = alert_row['customer_identifier']

    # 2. Verify client_profiles record exists (FK constraint requirement)
    profile_exists = await pool.fetchrow(
        "SELECT client_id FROM client_profiles WHERE client_id = $1",
        client_id
    )

    if not profile_exists:
        raise HTTPException(
            status_code=400,
            detail=f"Client profile must be fetched at least once before saving suitability data. Client ID: {client_id}"
        )

    # 3. Insert or update suitability data
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
