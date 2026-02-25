"""
Product comparison endpoints - triggers agent_two for product recommendations.
"""
import json
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.database import pool
from api.sureify_client import SureifyClient, SureifyAuthConfig

# Import profile endpoint to ensure data exists before agent_two call
import api.routers.profiles as profiles_module

# Add agents directory to path to import agent_two
_repo_root = Path(__file__).resolve().parent.parent.parent.parent
agents_dir = _repo_root / "agents"
if str(agents_dir) not in sys.path:
    sys.path.insert(0, str(agents_dir))

# Import agent_two modules
from agent_two.main import generate_product_recommendations
from agent_two_schemas import ProductRecommendation

router = APIRouter(prefix="/api/alerts", tags=["Compare"])


# Request/Response Models
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


def _convert_recommendation_to_product_option(rec: ProductRecommendation) -> ProductOption:
    """Convert agent_two ProductRecommendation to UI ProductOption format"""
    return ProductOption(
        name=rec.name,
        carrier=rec.carrier,
        rate=rec.rate,
        term=rec.term,
        surrenderPeriod=rec.surrenderPeriod,
        freeWithdrawal=rec.freeWithdrawal,
        guaranteedMinRate=rec.guaranteedMinRate,
        deathBenefit=None,  # Not in agent_two schema
        riders=None,  # Could parse from key_benefits
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

    # Extract clientId from alert_detail.policy.clientId
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
    # 1. Get alert and client info
    alert_data, client_id = await _get_alert_and_client(alert_id)

    # 2. Ensure profile data exists by calling profile endpoint
    # This handles DB-first with Sureify fallback, ensuring data is available for agent_two
    config = SureifyAuthConfig()
    sureify = SureifyClient(config)
    await sureify.authenticate()
    try:
        profile = await profiles_module.get_client_profile(client_id, sureify)
    finally:
        await sureify.close()

    # Profile data is now guaranteed to exist (either fetched from DB or Sureify)

    # 3. Call agent_two with empty changes (using existing profile from DB)
    changes_json = json.dumps({})

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

        # 4. Build current product from alert data
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

        # 5. Convert agent_two recommendations to alternatives
        alternatives: list[ProductOption] = []
        recommendations = result.get('recommendations', [])

        for rec_dict in recommendations[:3]:  # Max 3 alternatives
            try:
                rec = ProductRecommendation(**rec_dict)
                alternatives.append(_convert_recommendation_to_product_option(rec))
            except Exception:
                continue

        return ComparisonResult(
            comparisonData=ComparisonData(
                current=current_product,
                alternatives=alternatives,
                missingData=False
            )
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
    # 1. Get alert and client info
    alert_data, client_id = await _get_alert_and_client(alert_id)

    # 2. Validate selected products
    if not request.selectedProducts or len(request.selectedProducts) > 3:
        raise HTTPException(
            status_code=400,
            detail="Must provide 1-3 selected products"
        )

    # 3. Build current product from alert data
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

    # 4. Use selected products as alternatives
    # No need to call agent_two here - advisor manually selected these
    return ComparisonResult(
        comparisonData=ComparisonData(
            current=current_product,
            alternatives=request.selectedProducts,
            missingData=False
        )
    )
