"""
Product comparison endpoints - triggers agent_two for product recommendations.
"""
import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.database import pool
from api.sureify_client import SureifyClient, SureifyAuthConfig

import api.routers.profiles as profiles_module

AGENTS_URL = os.environ.get("AGENTS_URL", "http://agents:8000")

router = APIRouter(prefix="/api/alerts", tags=["Compare"])


class ProductOption(BaseModel):
    """Product option for comparison"""
    name: str
    carrier: str
    rate: str
    term: str | None = None
    premiumBonus: str | None = None
    surrenderPeriod: str | None = None
    surrenderCharge: str | None = None
    freeWithdrawal: str | None = None
    deathBenefit: str | None = None
    guaranteedMinRate: str | None = None
    riders: list[str] | None = None
    features: list[str] | None = None
    liquidity: str | None = None
    mvaPenalty: str | None = None
    licensingApproved: bool | None = None
    licensingDetails: str | None = None


class ComparisonData(BaseModel):
    """Comparison data with current product and alternatives"""
    current: ProductOption
    alternatives: list[ProductOption]
    missingData: bool


class ComparisonResult(BaseModel):
    """Result of comparison analysis"""
    comparisonData: ComparisonData


class RecompareRequest(BaseModel):
    """Request to recompare with selected products"""
    selectedProducts: list[ProductOption]


def _convert_recommendation_to_product_option(rec: dict) -> ProductOption:
    """Convert agent_two recommendation dict to UI ProductOption format"""
    return ProductOption(
        name=rec.get("name", "Unknown"),
        carrier=rec.get("carrier", "Unknown"),
        rate=rec.get("rate", "Unknown"),
        term=rec.get("term"),
        surrenderPeriod=rec.get("surrenderPeriod"),
        freeWithdrawal=rec.get("freeWithdrawal"),
        guaranteedMinRate=rec.get("guaranteedMinRate"),
        deathBenefit=None,
        riders=None,
        features=None,
        liquidity=None,
        mvaPenalty=None,
        licensingApproved=None,
        licensingDetails=None,
    )


async def _get_alert_and_client(alert_id: str) -> tuple[dict, str]:
    """Get alert data and extract client_id from alert_detail.policy.clientId"""
    alert_row = await pool.fetchrow(
        """
        SELECT customer_identifier, policy_id, client_name, carrier,
               current_value, current_rate, renewal_rate, alert_detail
        FROM alerts
        WHERE id = $1
        """,
        alert_id
    )

    if not alert_row:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

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

    return dict(alert_row), client_id


@router.post("/{alert_id}/compare", response_model=ComparisonResult)
async def run_comparison(alert_id: str):
    """
    Run comparison analysis using agent_two.

    Triggers product comparison using the client's saved profile parameters.
    Returns current product vs top 3 alternatives with rates, features, and chart data.
    """
    alert_data, client_id = await _get_alert_and_client(alert_id)

    config = SureifyAuthConfig()
    sureify = SureifyClient(config)
    await sureify.authenticate()
    try:
        await profiles_module.get_client_profile(client_id, sureify)
    finally:
        await sureify.close()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AGENTS_URL}/agent-two/recommendations",
                json={
                    "client_id": client_id,
                    "changes_json": "{}",
                    "alert_id": alert_id,
                    "use_llm": False,
                }
            )
            response.raise_for_status()
            result = response.json().get("result", {})

        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=f"Agent_two error: {result.get('message', 'Unknown error')}"
            )

        current_product = ProductOption(
            name=f"Current Policy {alert_data['policy_id']}",
            carrier=alert_data['carrier'],
            rate=alert_data.get('current_rate', 'Unknown'),
            term=None,
            surrenderPeriod=None,
            freeWithdrawal=None,
            deathBenefit=None,
            guaranteedMinRate=None,
        )

        alternatives: list[ProductOption] = []
        recommendations = result.get('recommendations', [])

        for rec_dict in recommendations[:3]:
            try:
                alternatives.append(_convert_recommendation_to_product_option(rec_dict))
            except Exception:
                continue

        return ComparisonResult(
            comparisonData=ComparisonData(
                current=current_product,
                alternatives=alternatives,
                missingData=False
            )
        )

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Agent service error: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Agent service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running comparison: {str(e)}"
        )


@router.post("/{alert_id}/compare/products", response_model=ComparisonResult)
async def recompare_with_products(alert_id: str, request: RecompareRequest):
    """
    Re-run comparison with selected products.

    Re-runs the comparison analysis using a specific set of products chosen by the
    advisor from the product shelf. Replaces the alternatives in the comparison while
    keeping the current policy.
    """
    alert_data, client_id = await _get_alert_and_client(alert_id)

    if not request.selectedProducts or len(request.selectedProducts) > 3:
        raise HTTPException(
            status_code=400,
            detail="Must provide 1-3 selected products"
        )

    current_product = ProductOption(
        name=f"Current Policy {alert_data['policy_id']}",
        carrier=alert_data['carrier'],
        rate=alert_data.get('current_rate', 'Unknown'),
        term=None,
        surrenderPeriod=None,
        freeWithdrawal=None,
        deathBenefit=None,
        guaranteedMinRate=None,
    )

    return ComparisonResult(
        comparisonData=ComparisonData(
            current=current_product,
            alternatives=request.selectedProducts,
            missingData=False
        )
    )
