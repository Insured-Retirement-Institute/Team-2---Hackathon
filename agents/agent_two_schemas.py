"""
Pydantic schemas for agentTwo: front-end changes (suitability, client goals, client profile),
product recommendation output, and storable payload (with explanations) for the database.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ---- Suitability (aligns with IRI SuitabilityData) ----
class SuitabilityChanges(BaseModel):
    """Changes to suitability form data (optional fields)."""
    clientObjectives: str | None = None
    riskTolerance: str | None = None
    timeHorizon: str | None = None
    liquidityNeeds: str | None = None
    taxConsiderations: str | None = None
    guaranteedIncome: str | None = None
    rateExpectations: str | None = None
    surrenderTimeline: str | None = None
    livingBenefits: list[str] | None = None
    advisorEligibility: str | None = None
    score: int | None = None
    isPrefilled: bool | None = None


# ---- Client goals (financial objectives, distribution, etc.) ----
class ClientGoalsChanges(BaseModel):
    """Changes to client goals (subset of comparison parameters)."""
    financialObjectives: str | None = None
    distributionPlan: str | None = None
    ownedAssets: str | None = None
    timeToFirstDistribution: str | None = None
    expectedHoldingPeriod: str | None = None
    sourceOfFunds: str | None = None
    employmentStatus: str | None = None


# ---- Client profile (comparison parameters / demographics) ----
class ClientProfileChanges(BaseModel):
    """Changes to client profile (comparison parameters)."""
    residesInNursingHome: str | None = None  # yes | no
    hasLongTermCareInsurance: str | None = None
    hasMedicareSupplemental: str | None = None
    grossIncome: str | None = None
    disposableIncome: str | None = None
    taxBracket: str | None = None
    householdLiquidAssets: str | None = None
    monthlyLivingExpenses: str | None = None
    totalAnnuityValue: str | None = None
    householdNetWorth: str | None = None
    anticipateExpenseIncrease: str | None = None
    anticipateIncomeDecrease: str | None = None
    anticipateLiquidAssetDecrease: str | None = None
    applyToMeansTestedBenefits: str | None = None


# ---- Front-end input: single JSON with optional sections ----
class ProfileChangesInput(BaseModel):
    """
    JSON from front-end with changes to suitability, client goals, and/or client profile.
    Only include keys that have changed; agentTwo merges with current DB state.
    """
    suitability: SuitabilityChanges | None = None
    client_goals: ClientGoalsChanges | None = Field(None, alias="clientGoals")
    client_profile: ClientProfileChanges | None = Field(None, alias="clientProfile")

    model_config = {"populate_by_name": True}


# ---- Reasons to switch products (pros + cons for display) ----
class ReasonsToSwitch(BaseModel):
    """Reasons why it makes sense to switch products. Display with + for pros, − for cons."""
    pros: list[str] = Field(
        default_factory=list,
        description="Benefits of switching (e.g. no new underwriting, surrender expired)",
    )
    cons: list[str] = Field(
        default_factory=list,
        description="Drawbacks or considerations (e.g. rate drop, missing higher rates)",
    )


# ---- Product recommendation output (one product option) ----
class ProductRecommendation(BaseModel):
    """A single product recommendation for the client."""
    product_id: str
    name: str
    carrier: str
    rate: str = Field(..., description="e.g. 4.25%")
    term: str | None = None
    surrenderPeriod: str | None = None
    freeWithdrawal: str | None = None
    guaranteedMinRate: str | None = None
    risk_profile: str | None = None
    suitable_for: str | None = None
    key_benefits: str | None = None
    match_reason: str | None = Field(None, description="Why this product was recommended")


# ---- Explanation of agentTwo's choices (for display and storage) ----
class ChoiceExplanation(BaseModel):
    """Structured explanation of how agentTwo chose recommendations. Stored with the run."""
    summary: str = Field(
        ...,
        description="Short summary of how recommendations were derived (e.g. data sources and criteria)",
    )
    data_sources_used: list[str] = Field(
        default_factory=list,
        description="Sources used: e.g. sureify_products, db_suitability, db_products",
    )
    choice_criteria: list[str] = Field(
        default_factory=list,
        description="Criteria applied: e.g. risk tolerance, time horizon, liquidity, financial objectives",
    )
    input_sections_received: list[str] = Field(
        default_factory=list,
        description="Which input sections were present: suitability, clientGoals, clientProfile",
    )


# ---- Storable payload: full JSON to persist in the database ----
class AgentTwoStorablePayload(BaseModel):
    """
    Single JSON payload that agentTwo produces for database storage.
    Contains run id, timestamp, client, input summary, explanation of choices, and recommendations.
    """
    run_id: str = Field(..., description="Unique id for this recommendation run (e.g. UUID)")
    created_at: str = Field(..., description="ISO 8601 timestamp when the run was produced")
    client_id: str
    input_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of incoming JSON (which sections were present; no PII). For audit.",
    )
    explanation: ChoiceExplanation = Field(
        ...,
        description="Structured explanation of agentTwo's choices (why these recommendations)",
    )
    recommendations: list[ProductRecommendation] = Field(
        ...,
        description="Recommended products with match_reason per item",
    )
    reasons_to_switch: ReasonsToSwitch | None = Field(
        None,
        description="Pros (+) and cons (−) for why it makes sense to switch products",
    )
    merged_profile_summary: dict[str, Any] | None = Field(
        None,
        description="Merged suitability + goals/profile used for recommendations (audit)",
    )
    iri_comparison_result: dict[str, Any] | None = Field(
        None,
        description="If IRI compare was run, the ComparisonResult (optional)",
    )


# ---- Full response for generate_product_recommendations ----
class ProductRecommendationsOutput(BaseModel):
    """Output of agentTwo product recommendations."""
    client_id: str
    merged_profile_summary: dict[str, Any] | None = Field(
        None, description="Summary of merged DB + changes used for recommendations"
    )
    recommendations: list[ProductRecommendation]
    explanation: ChoiceExplanation | None = Field(
        None,
        description="Structured explanation of agentTwo's choices (summary, data sources, criteria)",
    )
    reasons_to_switch: ReasonsToSwitch | None = Field(
        None,
        description="Pros (+) and cons (−) for why it makes sense to switch products",
    )
    storable_payload: AgentTwoStorablePayload | None = Field(
        None,
        description="Full payload to store in the database (run_id, created_at, explanation, recommendations)",
    )
    iri_comparison_result: dict[str, Any] | None = Field(
        None, description="If IRI compare was run, the ComparisonResult"
    )
