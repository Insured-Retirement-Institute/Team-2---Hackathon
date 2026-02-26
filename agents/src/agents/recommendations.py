"""
Product recommendation logic for agentTwo. Merges current DB state with front-end changes
and generates product recommendations. Prefers Sureify /puddle/products when present;
otherwise uses DB products table. Contextualizes recommendations using the incoming JSON
(suitability, client goals, client profile).
"""

from __future__ import annotations

from typing import Any

from agents.logging_config import get_logger

logger = get_logger(__name__)

from agents.agent_two_schemas import (
    ChoiceExplanation,
    ProductRecommendation,
    ProductRecommendationsOutput,
    ProfileChangesInput,
    ReasonsToSwitch,
)


def _sureify_product_to_canonical(p: dict[str, Any]) -> dict[str, Any]:
    """Normalize Sureify product to canonical shape for ProductRecommendation. Accepts Puddle ProductOption (from /puddle/productOption) already normalized by sureify_client, or legacy shape with attributes."""
    if p.get("product_id"):
        return p
    attrs = p.get("attributes") or []
    attr_map = {}
    for a in attrs:
        if isinstance(a, dict):
            k = (a.get("name") or a.get("key") or "").strip()
            v = a.get("value") or a.get("val")
            if k:
                attr_map[k.lower()] = v
        elif hasattr(a, "name") and hasattr(a, "value"):
            attr_map[(getattr(a, "name", "") or "").lower()] = getattr(a, "value", None)
    product_id = str(p.get("ID") or p.get("productCode") or "")
    name = str(p.get("name") or "Unknown")
    carrier = str(p.get("carrierCode") or p.get("carrier") or "")
    risk_profile = attr_map.get("riskprofile") or attr_map.get("risk_profile")
    return {
        "product_id": product_id,
        "name": name,
        "carrier": carrier,
        "rate": attr_map.get("rate") or "N/A",
        "risk_profile": risk_profile,
        "attributes_map": attr_map,
        "states": p.get("states"),
        "term": None,
        "surrenderPeriod": None,
        "freeWithdrawal": None,
        "guaranteedMinRate": None,
    }


def _build_match_reason_from_context(
    merged_suit: dict[str, Any],
    merged_goals: dict[str, Any],
) -> str:
    """Build human-readable match reason from incoming JSON context (suitability, goals, profile)."""
    reasons = []
    risk = (merged_suit.get("risk_tolerance") or "").strip()
    if risk:
        reasons.append(f"risk tolerance: {risk}")
    th = (merged_suit.get("time_horizon") or merged_suit.get("investment_horizon") or "").strip()
    if th:
        reasons.append(f"time horizon: {th}")
    liq = (merged_suit.get("liquidity_needs") or merged_suit.get("liquidity_importance") or "").strip()
    if liq:
        reasons.append(f"liquidity: {liq}")
    obj = (merged_suit.get("client_objectives") or merged_goals.get("financial_objectives") or "").strip()
    if obj:
        reasons.append(f"objectives: {obj[:80]}{'...' if len(obj) > 80 else ''}")
    hold = (merged_goals.get("expected_holding_period") or "").strip()
    if hold:
        reasons.append(f"holding period: {hold}")
    if not reasons:
        return "Recommended from Sureify product catalog based on profile."
    return "Contextualized from your profile: " + "; ".join(reasons)


def _build_reasons_to_switch(
    recommendations: list[ProductRecommendation],
    merged_suit: dict[str, Any],
    merged_goals: dict[str, Any],
    use_sureify: bool,
) -> ReasonsToSwitch:
    """
    Build pros (+) and cons (−) for why it makes sense to switch products.
    Example: +No new paperwork or underwriting; −Missing opportunity to capture higher market rates.
    """
    pros: list[str] = [
        "No new paperwork or underwriting",
        "Maintains existing carrier relationship",
        "Surrender period already expired or minimal remaining",
    ]

    # Cons: rate considerations from recommended products
    cons: list[str] = []
    rates: list[float] = []
    for r in recommendations:
        try:
            rate_str = (r.rate or "").replace("%", "").strip()
            if rate_str and rate_str != "N/A":
                rates.append(float(rate_str))
        except (ValueError, TypeError):
            pass
    if rates:
        max_rate = max(rates)
        min_rate = min(rates)
        if min_rate < max_rate:
            cons.append(f"Significant rate drop to guaranteed minimum {min_rate}%")
        if max_rate > 0:
            cons.append(f"Missing opportunity to capture higher market rates ({max_rate}% available)")
    elif recommendations:
        cons.append("Missing opportunity to capture higher market rates (check current product rates)")

    return ReasonsToSwitch(pros=pros, cons=cons)


def _build_choice_explanation(
    use_sureify: bool,
    merged_suit: dict[str, Any],
    merged_goals: dict[str, Any],
    changes: ProfileChangesInput,
    recommendation_count: int,
) -> ChoiceExplanation:
    """Build structured explanation of agentTwo's choices for storage and display."""
    data_sources_used = ["sureify_products"] if use_sureify else ["db_products"]
    if merged_suit or merged_goals:
        data_sources_used.append("db_suitability")
    criteria: list[str] = []
    if (merged_suit.get("risk_tolerance") or "").strip():
        criteria.append("risk tolerance")
    if (merged_suit.get("time_horizon") or merged_suit.get("investment_horizon") or "").strip():
        criteria.append("time horizon")
    if (merged_suit.get("liquidity_needs") or merged_suit.get("liquidity_importance") or "").strip():
        criteria.append("liquidity needs")
    if (merged_suit.get("client_objectives") or merged_goals.get("financial_objectives") or "").strip():
        criteria.append("financial objectives")
    if (merged_goals.get("expected_holding_period") or "").strip():
        criteria.append("expected holding period")
    if not criteria:
        criteria.append("product catalog match")
    input_sections: list[str] = []
    if changes.suitability:
        input_sections.append("suitability")
    if changes.client_goals:
        input_sections.append("clientGoals")
    if changes.client_profile:
        input_sections.append("clientProfile")
    catalog = "available product catalog" if use_sureify else "product catalog"
    summary = (
        f"Opportunity Generator produced {recommendation_count} opportunities presented from the {catalog}, "
        f"contextualized using: {', '.join(criteria)}. "
        f"Input sections received: {', '.join(input_sections) or 'none'}."
    )
    return ChoiceExplanation(
        summary=summary,
        data_sources_used=data_sources_used,
        choice_criteria=criteria,
        input_sections_received=input_sections,
    )


def _merge_suitability(
    db_profile: dict[str, Any] | None,
    changes: ProfileChangesInput,
) -> dict[str, Any]:
    """Merge DB suitability profile with suitability changes. DB keys match client_suitability_profiles columns."""
    out: dict[str, Any] = {}
    if db_profile:
        # Map DB columns to SuitabilityData-like keys where applicable
        out["risk_tolerance"] = db_profile.get("risk_tolerance")
        out["primary_objective"] = db_profile.get("primary_objective")
        out["secondary_objective"] = db_profile.get("secondary_objective")
        out["liquidity_importance"] = db_profile.get("liquidity_importance")
        out["investment_horizon"] = db_profile.get("investment_horizon")
        out["withdrawal_horizon"] = db_profile.get("withdrawal_horizon")
        out["current_income_need"] = db_profile.get("current_income_need")
        out["age"] = db_profile.get("age")
        out["state"] = db_profile.get("state")
    if changes.suitability:
        s = changes.suitability
        if s.riskTolerance is not None:
            out["risk_tolerance"] = s.riskTolerance
        if s.timeHorizon is not None:
            out["time_horizon"] = s.timeHorizon
        if s.liquidityNeeds is not None:
            out["liquidity_needs"] = s.liquidityNeeds
        if s.clientObjectives is not None:
            out["client_objectives"] = s.clientObjectives
    return out


def _merge_goals_and_profile(
    db_profile: dict[str, Any] | None,
    changes: ProfileChangesInput,
) -> dict[str, Any]:
    """Merge DB profile with client_goals and client_profile changes."""
    out: dict[str, Any] = {}
    if db_profile:
        out["annual_income_range"] = db_profile.get("annual_income_range")
        out["net_worth_range"] = db_profile.get("net_worth_range")
        out["liquid_net_worth_range"] = db_profile.get("liquid_net_worth_range")
        out["tax_bracket"] = db_profile.get("tax_bracket")
    if changes.client_goals:
        g = changes.client_goals
        if g.financialObjectives is not None:
            out["financial_objectives"] = g.financialObjectives
        if g.distributionPlan is not None:
            out["distribution_plan"] = g.distributionPlan
        if g.expectedHoldingPeriod is not None:
            out["expected_holding_period"] = g.expectedHoldingPeriod
    if changes.client_profile:
        p = changes.client_profile
        if p.grossIncome is not None:
            out["gross_income"] = p.grossIncome
        if p.householdNetWorth is not None:
            out["household_net_worth"] = p.householdNetWorth
        if p.householdLiquidAssets is not None:
            out["household_liquid_assets"] = p.householdLiquidAssets
        if p.taxBracket is not None:
            out["tax_bracket"] = p.taxBracket
    return out


def _format_rate(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"{value}%"
    return str(value)


def generate_recommendations(
    client_id: str,
    db_context: dict[str, Any],
    changes: ProfileChangesInput,
    alert_id: str | None = None,
    iri_comparison_result: dict[str, Any] | None = None,
    max_recommendations: int = 10,
) -> ProductRecommendationsOutput:
    """
    Build merged profile from DB + changes, then recommend products from the catalog.
    Optionally include IRI comparison result if run_iri_comparison was called.
    """
    logger.info("generate_recommendations: client_id=%s alert_id=%s", client_id, alert_id)
    clients = db_context.get("clients") or []
    profiles = db_context.get("client_suitability_profiles") or []
    products = db_context.get("products") or []

    # Resolve client: by client_account_number or client_name substring
    client_row: dict[str, Any] | None = None
    for c in clients:
        acct = (c.get("client_account_number") or "").strip()
        name = (c.get("client_name") or "").lower()
        if acct == client_id or client_id.lower() in name or client_id in acct:
            client_row = c
            break
    if not client_row and clients:
        client_row = clients[0]

    # Suitability profile for this client
    acct = (client_row or {}).get("client_account_number")
    db_suit = next(
        (p for p in profiles if p.get("client_account_number") == acct),
        None,
    )
    if not db_suit and profiles:
        db_suit = profiles[0]

    merged_suit = _merge_suitability(db_suit, changes)
    merged_goals = _merge_goals_and_profile(db_suit, changes)
    merged_profile_summary = {
        "suitability": merged_suit,
        "goals_and_profile": merged_goals,
    }

    # Prefer Sureify /puddle/products when present; else use DB products table
    sureify_products = db_context.get("sureify_products") or []
    use_sureify = len(sureify_products) > 0

    risk = (merged_suit.get("risk_tolerance") or "").lower()
    state = (merged_suit.get("state") or "").strip()
    recs: list[ProductRecommendation] = []

    if use_sureify:
        # Contextualize recommendations from Sureify products using incoming JSON (suitability, goals, profile)
        base_reason = _build_match_reason_from_context(merged_suit, merged_goals)
        for p in sureify_products:
            canon = _sureify_product_to_canonical(p)
            if not canon.get("product_id"):
                continue
            product_risk = (str(canon.get("risk_profile") or "")).lower()
            if risk and product_risk and risk not in product_risk and product_risk not in risk:
                pass  # still include; match_reason explains context
            rate_str = canon.get("rate") or "N/A"
            if rate_str != "N/A" and "%" not in str(rate_str):
                rate_str = f"{rate_str}%"
            recs.append(
                ProductRecommendation(
                    product_id=canon["product_id"],
                    name=canon["name"],
                    carrier=canon["carrier"],
                    rate=rate_str,
                    term=canon.get("term"),
                    surrenderPeriod=canon.get("surrenderPeriod"),
                    freeWithdrawal=canon.get("freeWithdrawal"),
                    guaranteedMinRate=canon.get("guaranteedMinRate"),
                    risk_profile=canon.get("risk_profile"),
                    suitable_for=None,
                    key_benefits=None,
                    match_reason=base_reason,
                )
            )
    else:
        # DB products (legacy shape)
        for p in products:
            if not p.get("product_id"):
                continue
            product_risk = (p.get("risk_profile") or "").lower()
            rate = _format_rate(p.get("current_fixed_rate") or p.get("guaranteed_minimum_rate"))
            recs.append(
                ProductRecommendation(
                    product_id=str(p.get("product_id", "")),
                    name=str(p.get("product_name", "Unknown")),
                    carrier=str(p.get("carrier", "")),
                    rate=rate,
                    term=None,
                    surrenderPeriod=str(p.get("cdsc_years", "")) if p.get("cdsc_years") is not None else None,
                    freeWithdrawal=_format_rate(p.get("free_withdrawal_percent")),
                    guaranteedMinRate=_format_rate(p.get("guaranteed_minimum_rate")),
                    risk_profile=p.get("risk_profile"),
                    suitable_for=p.get("suitable_for"),
                    key_benefits=p.get("key_benefits"),
                    match_reason=_build_match_reason_from_context(merged_suit, merged_goals),
                )
            )

    # Sort by rate (best first) when numeric, else keep order; take top N
    def rate_sort_key(r: ProductRecommendation) -> float:
        try:
            return float(str(r.rate).replace("%", "").strip())
        except (ValueError, AttributeError):
            return 0.0

    recs.sort(key=rate_sort_key, reverse=True)
    recs = recs[:max_recommendations]
    logger.info("generate_recommendations: produced %d recommendations (source=%s)", len(recs), "sureify" if use_sureify else "db")

    explanation = _build_choice_explanation(
        use_sureify, merged_suit, merged_goals, changes, len(recs)
    )
    reasons_to_switch = _build_reasons_to_switch(recs, merged_suit, merged_goals, use_sureify)

    return ProductRecommendationsOutput(
        client_id=client_id,
        merged_profile_summary=merged_profile_summary,
        recommendations=recs,
        explanation=explanation,
        reasons_to_switch=reasons_to_switch,
        storable_payload=None,  # Built in agent_two.py with run_id and created_at
        iri_comparison_result=iri_comparison_result,
    )
