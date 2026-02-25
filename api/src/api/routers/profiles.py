"""
Client Profile endpoints - manages client comparison parameters and suitability data.

Logic:
- GET: Check DB first (JOIN client_profiles + client_suitability_data), else fetch from Sureify
- PUT: Save ComparisonParameters to client_profiles table
- PUT /alerts/{alertId}/suitability: Update suitability_data linked via alert's customer_identifier
"""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.sureify_client import SureifyClient, SureifyAuthConfig
from api.database import pool

router = APIRouter(prefix="/api/clients", tags=["Client Profiles"])


class ComparisonParameters(BaseModel):
    """Client comparison parameters (financial profile)"""
    # Profile
    residesInNursingHome: str | None = None
    hasLongTermCareInsurance: str | None = None
    hasMedicareSupplemental: str | None = None
    # Financial
    grossIncome: str | None = None
    disposableIncome: str | None = None
    taxBracket: str | None = None
    householdLiquidAssets: str | None = None
    monthlyLivingExpenses: str | None = None
    totalAnnuityValue: str | None = None
    householdNetWorth: str | None = None
    # Anticipated Changes
    anticipateExpenseIncrease: str | None = None
    anticipateIncomeDecrease: str | None = None
    anticipateLiquidAssetDecrease: str | None = None
    # Objectives & Planning
    financialObjectives: str | None = None
    distributionPlan: str | None = None
    ownedAssets: str | None = None
    timeToFirstDistribution: str | None = None
    expectedHoldingPeriod: str | None = None
    sourceOfFunds: str | None = None
    employmentStatus: str | None = None
    applyToMeansTestedBenefits: str | None = None


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


class ClientProfile(BaseModel):
    """Full client profile including parameters and suitability"""
    clientId: str
    clientName: str
    parameters: ComparisonParameters | None = None
    suitability: SuitabilityData | None = None


async def get_sureify_client():
    """Dependency to get authenticated Sureify client"""
    config = SureifyAuthConfig()
    client = SureifyClient(config)
    await client.authenticate()
    try:
        yield client
    finally:
        await client.close()


SureifyDep = Annotated[SureifyClient, Depends(get_sureify_client)]


@router.get("/{clientId}/profile", response_model=ClientProfile)
async def get_client_profile(clientId: str, sureify: SureifyDep):
    """
    Get client profile with comparison parameters and suitability data.

    Logic:
    1. Check if data exists in DB (JOIN client_profiles + client_suitability_data)
    2. If exists: Return merged data from both tables
    3. If not: Fetch from Sureify /puddle/clientProfile (includes both profile + suitability)
    """
    # 1. Check database for existing profile and suitability data
    profile_row = await pool.fetchrow(
        """
        SELECT
            client_id,
            client_name,
            resides_in_nursing_home,
            has_long_term_care_insurance,
            has_medicare_supplemental,
            gross_income,
            disposable_income,
            tax_bracket,
            household_liquid_assets,
            monthly_living_expenses,
            total_annuity_value,
            household_net_worth,
            anticipate_expense_increase,
            anticipate_income_decrease,
            anticipate_liquid_asset_decrease,
            financial_objectives,
            distribution_plan,
            owned_assets,
            time_to_first_distribution,
            expected_holding_period,
            source_of_funds,
            employment_status,
            apply_to_means_tested_benefits
        FROM client_profiles
        WHERE client_id = $1
        """,
        clientId
    )

    suitability_row = await pool.fetchrow(
        """
        SELECT
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
            is_prefilled
        FROM client_suitability_data
        WHERE client_id = $1
        """,
        clientId
    )

    # 2. If data exists in DB, merge and return
    if profile_row:
        parameters = ComparisonParameters(
            residesInNursingHome=profile_row['resides_in_nursing_home'],
            hasLongTermCareInsurance=profile_row['has_long_term_care_insurance'],
            hasMedicareSupplemental=profile_row['has_medicare_supplemental'],
            grossIncome=profile_row['gross_income'],
            disposableIncome=profile_row['disposable_income'],
            taxBracket=profile_row['tax_bracket'],
            householdLiquidAssets=profile_row['household_liquid_assets'],
            monthlyLivingExpenses=profile_row['monthly_living_expenses'],
            totalAnnuityValue=profile_row['total_annuity_value'],
            householdNetWorth=profile_row['household_net_worth'],
            anticipateExpenseIncrease=profile_row['anticipate_expense_increase'],
            anticipateIncomeDecrease=profile_row['anticipate_income_decrease'],
            anticipateLiquidAssetDecrease=profile_row['anticipate_liquid_asset_decrease'],
            financialObjectives=profile_row['financial_objectives'],
            distributionPlan=profile_row['distribution_plan'],
            ownedAssets=profile_row['owned_assets'],
            timeToFirstDistribution=profile_row['time_to_first_distribution'],
            expectedHoldingPeriod=profile_row['expected_holding_period'],
            sourceOfFunds=profile_row['source_of_funds'],
            employmentStatus=profile_row['employment_status'],
            applyToMeansTestedBenefits=profile_row['apply_to_means_tested_benefits']
        )

        suitability = None
        if suitability_row:
            suitability = SuitabilityData(
                clientObjectives=suitability_row['client_objectives'],
                riskTolerance=suitability_row['risk_tolerance'],
                timeHorizon=suitability_row['time_horizon'],
                liquidityNeeds=suitability_row['liquidity_needs'],
                taxConsiderations=suitability_row['tax_considerations'],
                guaranteedIncome=suitability_row['guaranteed_income'],
                rateExpectations=suitability_row['rate_expectations'],
                surrenderTimeline=suitability_row['surrender_timeline'],
                livingBenefits=suitability_row['living_benefits'],
                advisorEligibility=suitability_row['advisor_eligibility'],
                score=suitability_row['score'],
                isPrefilled=suitability_row['is_prefilled']
            )

        return ClientProfile(
            clientId=profile_row['client_id'],
            clientName=profile_row['client_name'],
            parameters=parameters,
            suitability=suitability
        )

    # 3. No data in DB - fetch from Sureify /puddle/clientProfile
    try:
        # Call Sureify puddle API /clientProfile endpoint
        response = await sureify._get(f"/puddle/clientProfile?clientId={clientId}", {})

        if not response or "clientProfiles" not in response:
            raise HTTPException(status_code=404, detail=f"Client {clientId} not found in Sureify")

        # Extract client profile data
        client_profiles = response.get("clientProfiles", [])
        if not client_profiles:
            raise HTTPException(status_code=404, detail=f"Client {clientId} not found in Sureify")

        client_data = client_profiles[0]

        # Also fetch suitability data from /puddle/suitabilityData
        suitability_response = await sureify._get(f"/puddle/suitabilityData?clientId={clientId}", {})
        suitability_list = suitability_response.get("suitabilityData", []) if suitability_response else []
        suitability_data = suitability_list[0] if suitability_list else None

        # Build response matching the format
        parameters_dict = client_data.get("parameters", {})
        parameters = ComparisonParameters(**parameters_dict) if parameters_dict else None

        suitability = None
        if suitability_data:
            suitability = SuitabilityData(**suitability_data)

        return ClientProfile(
            clientId=client_data.get("clientId", clientId),
            clientName=client_data.get("clientName", ""),
            parameters=parameters,
            suitability=suitability
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching client profile: {str(e)}")


@router.put("/{clientId}/profile")
async def save_client_profile(
    clientId: str,
    parameters: ComparisonParameters
):
    """
    Save/update client comparison parameters.

    Called when advisor updates profile in the Compare tab.
    Stores data in client_profiles table.
    """
    # Check if profile exists first to get client_name, or use a default
    existing = await pool.fetchrow(
        "SELECT client_name FROM client_profiles WHERE client_id = $1",
        clientId
    )

    client_name = existing['client_name'] if existing else f"Client {clientId}"

    await pool.execute(
        """
        INSERT INTO client_profiles (
            client_id,
            client_name,
            resides_in_nursing_home,
            has_long_term_care_insurance,
            has_medicare_supplemental,
            gross_income,
            disposable_income,
            tax_bracket,
            household_liquid_assets,
            monthly_living_expenses,
            total_annuity_value,
            household_net_worth,
            anticipate_expense_increase,
            anticipate_income_decrease,
            anticipate_liquid_asset_decrease,
            financial_objectives,
            distribution_plan,
            owned_assets,
            time_to_first_distribution,
            expected_holding_period,
            source_of_funds,
            employment_status,
            apply_to_means_tested_benefits,
            updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, now())
        ON CONFLICT (client_id) DO UPDATE SET
            resides_in_nursing_home = COALESCE(EXCLUDED.resides_in_nursing_home, client_profiles.resides_in_nursing_home),
            has_long_term_care_insurance = COALESCE(EXCLUDED.has_long_term_care_insurance, client_profiles.has_long_term_care_insurance),
            has_medicare_supplemental = COALESCE(EXCLUDED.has_medicare_supplemental, client_profiles.has_medicare_supplemental),
            gross_income = COALESCE(EXCLUDED.gross_income, client_profiles.gross_income),
            disposable_income = COALESCE(EXCLUDED.disposable_income, client_profiles.disposable_income),
            tax_bracket = COALESCE(EXCLUDED.tax_bracket, client_profiles.tax_bracket),
            household_liquid_assets = COALESCE(EXCLUDED.household_liquid_assets, client_profiles.household_liquid_assets),
            monthly_living_expenses = COALESCE(EXCLUDED.monthly_living_expenses, client_profiles.monthly_living_expenses),
            total_annuity_value = COALESCE(EXCLUDED.total_annuity_value, client_profiles.total_annuity_value),
            household_net_worth = COALESCE(EXCLUDED.household_net_worth, client_profiles.household_net_worth),
            anticipate_expense_increase = COALESCE(EXCLUDED.anticipate_expense_increase, client_profiles.anticipate_expense_increase),
            anticipate_income_decrease = COALESCE(EXCLUDED.anticipate_income_decrease, client_profiles.anticipate_income_decrease),
            anticipate_liquid_asset_decrease = COALESCE(EXCLUDED.anticipate_liquid_asset_decrease, client_profiles.anticipate_liquid_asset_decrease),
            financial_objectives = COALESCE(EXCLUDED.financial_objectives, client_profiles.financial_objectives),
            distribution_plan = COALESCE(EXCLUDED.distribution_plan, client_profiles.distribution_plan),
            owned_assets = COALESCE(EXCLUDED.owned_assets, client_profiles.owned_assets),
            time_to_first_distribution = COALESCE(EXCLUDED.time_to_first_distribution, client_profiles.time_to_first_distribution),
            expected_holding_period = COALESCE(EXCLUDED.expected_holding_period, client_profiles.expected_holding_period),
            source_of_funds = COALESCE(EXCLUDED.source_of_funds, client_profiles.source_of_funds),
            employment_status = COALESCE(EXCLUDED.employment_status, client_profiles.employment_status),
            apply_to_means_tested_benefits = COALESCE(EXCLUDED.apply_to_means_tested_benefits, client_profiles.apply_to_means_tested_benefits),
            updated_at = now()
        """,
        clientId,
        client_name,
        parameters.residesInNursingHome,
        parameters.hasLongTermCareInsurance,
        parameters.hasMedicareSupplemental,
        parameters.grossIncome,
        parameters.disposableIncome,
        parameters.taxBracket,
        parameters.householdLiquidAssets,
        parameters.monthlyLivingExpenses,
        parameters.totalAnnuityValue,
        parameters.householdNetWorth,
        parameters.anticipateExpenseIncrease,
        parameters.anticipateIncomeDecrease,
        parameters.anticipateLiquidAssetDecrease,
        parameters.financialObjectives,
        parameters.distributionPlan,
        parameters.ownedAssets,
        parameters.timeToFirstDistribution,
        parameters.expectedHoldingPeriod,
        parameters.sourceOfFunds,
        parameters.employmentStatus,
        parameters.applyToMeansTestedBenefits
    )

    return {"success": True, "message": "Profile saved"}
