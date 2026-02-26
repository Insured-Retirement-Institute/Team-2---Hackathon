"""
Action tab endpoints - disclosures and transaction submission.
"""
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api import database
from agents.agent_two.main import generate_product_recommendations

router = APIRouter(prefix="/alerts", tags=["Action"])


# Request/Response Models
class DisclosureRequest(BaseModel):
    """Request to save disclosure acknowledgments"""
    acknowledgedIds: list[str]


class TransactionRequest(BaseModel):
    """Request to submit a transaction"""
    type: str  # "renew" or "replace"
    rationale: str
    clientStatement: str


class SubmissionStatus(BaseModel):
    """Submission status entry"""
    status: str  # received, in-review, nigo, approved, issued
    timestamp: str
    notes: str | None = None


class SubmissionData(BaseModel):
    """Transaction submission response"""
    submissionId: str
    submittedDate: str
    carrier: str
    transactionType: str
    currentStatus: SubmissionStatus
    statusHistory: list[SubmissionStatus]
    nigoIssues: list[dict] | None = None


@router.put("/{alert_id}/disclosures")
async def save_disclosures(
    alert_id: str,
    request: DisclosureRequest
):
    """
    Save disclosure acknowledgments for an alert.

    Saves which disclosure items have been acknowledged by the advisor.
    """
    # Verify alert exists
    alert_row = await database.pool.fetchrow(
        "SELECT id FROM hackathon.alerts WHERE id = $1",
        alert_id
    )

    if not alert_row:
        raise HTTPException(
            status_code=404,
            detail=f"Alert {alert_id} not found"
        )

    # Store acknowledged disclosure IDs in alert_detail JSONB
    await database.pool.execute(
        """
        UPDATE hackathon.alerts
        SET alert_detail = COALESCE(alert_detail, '{}'::jsonb) ||
            jsonb_build_object('acknowledgedDisclosures', $1::jsonb)
        WHERE id = $2
        """,
        json.dumps(request.acknowledgedIds),
        alert_id
    )

    return {
        "success": True,
        "message": f"Saved {len(request.acknowledgedIds)} disclosure acknowledgments"
    }


@router.post("/{alert_id}/transaction", response_model=SubmissionData)
async def submit_transaction(
    alert_id: str,
    request: TransactionRequest
):
    """
    Submit transaction for an alert.

    Calls agent_two to generate transaction submission data including
    submission ID, status tracking, and any NIGO (Not In Good Order) issues.
    """
    # 1. Get alert data
    alert_row = await database.pool.fetchrow(
        """
        SELECT policy_id, client_name, carrier, alert_detail
        FROM hackathon.alerts
        WHERE id = $1
        """,
        alert_id
    )

    if not alert_row:
        raise HTTPException(
            status_code=404,
            detail=f"Alert {alert_id} not found"
        )

    # 2. Extract clientId from alert_detail
    alert_detail = alert_row.get('alert_detail')
    if not alert_detail:
        raise HTTPException(
            status_code=400,
            detail=f"Alert {alert_id} has no alert_detail data"
        )

    # Handle case where alert_detail is stored as JSON string
    if isinstance(alert_detail, str):
        alert_detail = json.loads(alert_detail)

    policy_data = alert_detail.get('policy', {})
    client_id = policy_data.get('clientId')

    if not client_id:
        raise HTTPException(
            status_code=400,
            detail=f"Alert {alert_id} has no clientId in policy data"
        )

    # 3. Call agent_two to generate submission data
    # Pass transaction details in changes_json
    changes_json = json.dumps({
        "transaction_type": request.type,
        "rationale": request.rationale,
        "client_statement": request.clientStatement
    })

    try:
        result_json = generate_product_recommendations(
            changes_json=changes_json,
            client_id=client_id,
            alert_id=alert_id
        )

        result = json.loads(result_json)

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=f"Agent_two error: {result.get('message', 'Unknown error')}"
            )

        # 4. Generate submission data
        # For now, create a mock submission response
        # In production, this would come from agent_two or be stored in DB
        import uuid
        from datetime import datetime, timezone

        submission_id = f"SUB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        submitted_date = datetime.now(timezone.utc).isoformat()

        current_status = SubmissionStatus(
            status="received",
            timestamp=submitted_date,
            notes=f"{request.type.capitalize()} transaction submitted successfully"
        )

        return SubmissionData(
            submissionId=submission_id,
            submittedDate=submitted_date,
            carrier=alert_row['carrier'],
            transactionType=request.type,
            currentStatus=current_status,
            statusHistory=[current_status],
            nigoIssues=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting transaction: {str(e)}"
        )
