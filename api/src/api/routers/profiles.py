"""
Client Profile endpoints - manages client comparison parameters and suitability data.

Logic:
- GET: Check DB first (JOIN client_profiles + client_suitability_data), else fetch from Sureify
- PUT: Save ComparisonParameters to client_profiles table
- PUT /alerts/{alertId}/suitability: Update suitability_data linked via alert's customer_identifier
"""
from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Request
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


async def get_sureify_client() -> AsyncGenerator[SureifyClient, None]:
    config = SureifyAuthConfig()
    client = SureifyClient(config)
    await client.authenticate()
    try:
        yield client
    finally:
        await client.close()


SureifyDep = Annotated[SureifyClient, Depends(get_sureify_client)]


@router.get("/{clientId}/profile", response_model=ClientProfile)
async def get_client_profile(
    clientId: Annotated[str, Path(description="Client identifier", example="Marty McFly")],
    request: Request
):
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

    # 3. No data in DB - fetch from passthrough endpoints (which work!)
    try:
        # Build URL for passthrough endpoint (internal call)
        base_url = str(request.base_url).rstrip('/')

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch all client profiles from passthrough
            profiles_response = await client.get(f"{base_url}/passthrough/client-profiles")
            if profiles_response.status_code != 200:
                raise HTTPException(status_code=profiles_response.status_code,
                                  detail="Failed to fetch client profiles from Sureify")

            profiles_data = profiles_response.json()
            client_data = next((p for p in profiles_data if p.get('clientId') == clientId), None)

            if not client_data:
                raise HTTPException(status_code=404, detail=f"Client {clientId} not found in Sureify")

            # Fetch suitability data from passthrough
            suitability_response = await client.get(f"{base_url}/passthrough/suitability-data")
            suitability_list = suitability_response.json() if suitability_response.status_code == 200 else []
            suitability_data = next((s for s in suitability_list if s.get('clientId') == clientId), None)

        # Build response objects from JSON data
        parameters = None
        params_raw = client_data.get('parameters')
        if params_raw:
            def get_value(field):
                """Extract value from enum-like field or return as-is"""
                if isinstance(field, dict) and 'value' in field:
                    return field['value']
                return field

            parameters = ComparisonParameters(
                residesInNursingHome=get_value(params_raw.get('residesInNursingHome')),
                hasLongTermCareInsurance=get_value(params_raw.get('hasLongTermCareInsurance')),
                hasMedicareSupplemental=get_value(params_raw.get('hasMedicareSupplemental')),
                grossIncome=params_raw.get('grossIncome'),
                disposableIncome=params_raw.get('disposableIncome'),
                taxBracket=params_raw.get('taxBracket'),
                householdLiquidAssets=params_raw.get('householdLiquidAssets'),
                monthlyLivingExpenses=params_raw.get('monthlyLivingExpenses'),
                totalAnnuityValue=params_raw.get('totalAnnuityValue'),
                householdNetWorth=params_raw.get('householdNetWorth'),
                anticipateExpenseIncrease=get_value(params_raw.get('anticipateExpenseIncrease')),
                anticipateIncomeDecrease=get_value(params_raw.get('anticipateIncomeDecrease')),
                anticipateLiquidAssetDecrease=get_value(params_raw.get('anticipateLiquidAssetDecrease')),
                financialObjectives=params_raw.get('financialObjectives'),
                distributionPlan=params_raw.get('distributionPlan'),
                ownedAssets=params_raw.get('ownedAssets'),
                timeToFirstDistribution=params_raw.get('timeToFirstDistribution'),
                expectedHoldingPeriod=params_raw.get('expectedHoldingPeriod'),
                sourceOfFunds=params_raw.get('sourceOfFunds'),
                employmentStatus=params_raw.get('employmentStatus'),
                applyToMeansTestedBenefits=get_value(params_raw.get('applyToMeansTestedBenefits')),
            )

        suitability = None
        if suitability_data:
            suitability = SuitabilityData(
                clientObjectives=suitability_data.get('clientObjectives'),
                riskTolerance=suitability_data.get('riskTolerance'),
                timeHorizon=suitability_data.get('timeHorizon'),
                liquidityNeeds=suitability_data.get('liquidityNeeds'),
                taxConsiderations=suitability_data.get('taxConsiderations'),
                guaranteedIncome=suitability_data.get('guaranteedIncome'),
                rateExpectations=suitability_data.get('rateExpectations'),
                surrenderTimeline=suitability_data.get('surrenderTimeline'),
                livingBenefits=suitability_data.get('livingBenefits', []),
                advisorEligibility=suitability_data.get('advisorEligibility'),
                score=suitability_data.get('score', 0),
                isPrefilled=suitability_data.get('isPrefilled', False),
            )

        # 4. SAVE TO DATABASE for future requests
        # Save profile data
        if parameters:
            await pool.execute(
                """
                INSERT INTO client_profiles (
                    client_id, client_name,
                    resides_in_nursing_home, has_long_term_care_insurance, has_medicare_supplemental,
                    gross_income, disposable_income, tax_bracket,
                    household_liquid_assets, monthly_living_expenses, total_annuity_value, household_net_worth,
                    anticipate_expense_increase, anticipate_income_decrease, anticipate_liquid_asset_decrease,
                    financial_objectives, distribution_plan, owned_assets,
                    time_to_first_distribution, expected_holding_period, source_of_funds,
                    employment_status, apply_to_means_tested_benefits,
                    updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, now())
                ON CONFLICT (client_id) DO NOTHING
                """,
                client_data.get('clientId'),
                client_data.get('clientName'),
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

        # Save suitability data
        if suitability:
            await pool.execute(
                """
                INSERT INTO client_suitability_data (
                    client_id,
                    client_objectives, risk_tolerance, time_horizon, liquidity_needs,
                    tax_considerations, guaranteed_income, rate_expectations, surrender_timeline,
                    living_benefits, advisor_eligibility, score, is_prefilled,
                    updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, now())
                ON CONFLICT (client_id) DO NOTHING
                """,
                client_data.get('clientId'),
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

        return ClientProfile(
            clientId=client_data.get('clientId'),
            clientName=client_data.get('clientName'),
            parameters=parameters,
            suitability=suitability
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching client profile: {str(e)}")


@router.put("/{clientId}/profile")
async def save_client_profile(
    clientId: Annotated[str, Path(description="Client identifier", example="Marty McFly")],
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


@router.get("/{clientId}/policies/{policyId}")
async def get_policy_data(
    clientId: Annotated[str, Path(description="Client identifier", example="Marty McFly")],
    policyId: Annotated[str, Path(description="Policy/contract identifier", example="POL-001")],
    request: Request
):
    """
    Get full policy data for a specific client and policy combination.

    Calls /passthrough/policy-data endpoint and filters for the specific policy.
    """
    try:
        # Build URL for passthrough endpoint (internal call)
        base_url = str(request.base_url).rstrip('/')

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch all policy data from passthrough
            response = await client.get(f"{base_url}/passthrough/policy-data")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                  detail="Failed to fetch policy data from Sureify")

            policy_data_list = response.json()

            # Find the specific policy matching both clientId and policyId
            matching_policy = None
            for policy in policy_data_list:
                # Check if this policy matches both clientId and contractId (policyId)
                if policy.get('clientId') == clientId and policy.get('contractId') == policyId:
                    matching_policy = policy
                    break

            if not matching_policy:
                raise HTTPException(
                    status_code=404,
                    detail=f"Policy {policyId} not found for client {clientId}"
                )

            return matching_policy

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching policy data: {str(e)}"
        )


@router.put("/{clientId}/suitability")
async def save_suitability(
    clientId: Annotated[str, Path(description="Client identifier", example="Marty McFly")],
    suitability: SuitabilityData
):
    """
    Save suitability data for a client.

    Logic:
    1. Use clientId directly (passed in path)
    2. Verify client_profiles record exists (FK constraint requirement)
    3. Insert or update suitability data in client_suitability_data table
    """
    # 1. Verify client_profiles record exists (FK constraint requirement)
    profile_exists = await pool.fetchrow(
        "SELECT client_id FROM client_profiles WHERE client_id = $1",
        clientId
    )

    if not profile_exists:
        raise HTTPException(
            status_code=400,
            detail=f"Client profile must be fetched at least once before saving suitability data. Client ID: {clientId}"
        )

    # 2. Insert or update suitability data
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
        clientId,
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

    return {"success": True, "message": "Suitability saved"}
