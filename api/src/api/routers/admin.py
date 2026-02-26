"""
Admin endpoints for triggering background processes and system operations.
"""
import os
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["Admin Operations"])


class TriggerAlertsRequest(BaseModel):
    customer_identifier: str = "Marty McFly"


class TriggerAlertsResponse(BaseModel):
    success: bool
    message: str
    created: int
    errors: list[str] | None = None


@router.post("/trigger-alerts", response_model=TriggerAlertsResponse)
async def trigger_alerts_generation(request: TriggerAlertsRequest):
    """
    Trigger agent_one to generate alerts for a customer.

    This endpoint acts as a proxy to the agents service, allowing external
    callers to trigger alert generation without direct access to the agents service.

    Flow:
    1. API receives request with customer_identifier
    2. API forwards to agents service (internal K8s call)
    3. Agent one fetches policies and applies business logic
    4. Agent one POSTs alerts to API /api/alerts endpoint
    5. API returns success response

    Example:
        POST /api/admin/trigger-alerts
        {
            "customer_identifier": "Marty McFly"
        }

    Returns:
        {
            "success": true,
            "message": "Successfully created 5 alerts",
            "created": 5,
            "errors": null
        }
    """
    agents_url = os.environ.get("AGENTS_URL", "http://agents:80")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{agents_url}/agent-one/create-alerts",
                json={"customer_identifier": request.customer_identifier},
            )

            if response.status_code == 200:
                result = response.json()
                return TriggerAlertsResponse(
                    success=result.get("success", True),
                    message=result.get("message", "Alerts created successfully"),
                    created=result.get("created", 0),
                    errors=result.get("errors"),
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Agent service returned error: {response.text}",
                )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to agents service: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/agents")
async def check_agents_health() -> dict[str, Any]:
    """
    Check health of the agents service.

    Returns the health status and available endpoints from the agents service.
    """
    agents_url = os.environ.get("AGENTS_URL", "http://agents:80")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{agents_url}/health")

            if response.status_code == 200:
                return {
                    "agents_service": "healthy",
                    "agents_url": agents_url,
                    "response": response.json(),
                }
            else:
                return {
                    "agents_service": "unhealthy",
                    "agents_url": agents_url,
                    "status_code": response.status_code,
                }

    except httpx.RequestError as e:
        return {
            "agents_service": "unreachable",
            "agents_url": agents_url,
            "error": str(e),
        }
