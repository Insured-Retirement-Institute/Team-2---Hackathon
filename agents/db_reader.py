"""
Sync database reader for agentTwo. Reads current clients, suitability profiles,
contract summary, and products. Uses DATABASE_URL or RDS* env vars.
"""

from __future__ import annotations

import os
from typing import Any

# Optional: only needed when DATABASE_URL or RDS* are set
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None  # type: ignore
    RealDictCursor = None  # type: ignore


def _get_connection_params() -> dict[str, str] | None:
    url = os.environ.get("DATABASE_URL")
    if url and url.strip() and url != "postgresql://":
        return {"dsn": url}
    host = os.environ.get("RDSHOST")
    user = os.environ.get("RDS_USER")
    password = os.environ.get("RDS_PASSWORD")
    dbname = os.environ.get("RDS_DB", "postgres")
    if host and user and password:
        return {
            "host": host,
            "user": user,
            "password": password,
            "dbname": dbname,
        }
    return None


def get_all_clients() -> list[dict[str, Any]]:
    """Return all rows from clients table. Empty list if DB not configured or error."""
    params = _get_connection_params()
    if not params or psycopg2 is None:
        return []
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT client_account_number, client_name, process_dt FROM clients ORDER BY client_name")
                return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def get_all_client_suitability_profiles() -> list[dict[str, Any]]:
    """Return all rows from client_suitability_profiles. Empty list if DB not configured or error."""
    params = _get_connection_params()
    if not params or psycopg2 is None:
        return []
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT client_account_number, age, life_stage, marital_status, dependents,
                           risk_tolerance, investment_experience, volatility_comfort,
                           primary_objective, secondary_objective, liquidity_importance,
                           investment_horizon, withdrawal_horizon, current_income_need,
                           annual_income_range, net_worth_range, liquid_net_worth_range,
                           tax_bracket, retirement_target_year, state, citizenship,
                           advisory_model, is_fee_based_account
                    FROM client_suitability_profiles
                    """
                )
                return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def get_contract_summary(client_id: str | None = None) -> list[dict[str, Any]]:
    """Return contract_summary rows, optionally filtered by client (owner_name / client_id substring)."""
    params = _get_connection_params()
    if not params or psycopg2 is None:
        return []
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if client_id:
                    cur.execute(
                        "SELECT * FROM contract_summary WHERE owner_name ILIKE %s LIMIT 500",
                        (f"%{client_id}%",),
                    )
                else:
                    cur.execute("SELECT * FROM contract_summary LIMIT 500")
                return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def get_all_products() -> list[dict[str, Any]]:
    """Return all rows from products table (product catalog for recommendations)."""
    params = _get_connection_params()
    if not params or psycopg2 is None:
        return []
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT product_id, carrier, product_name, product_type, issue_year,
                           available_states, guaranteed_minimum_rate, current_fixed_rate,
                           risk_profile, age_min, age_max, suitable_for, key_benefits,
                           can_sell, compliance_notes
                    FROM products
                    WHERE can_sell = true
                    ORDER BY current_fixed_rate DESC NULLS LAST
                    """
                )
                return [dict(r) for r in cur.fetchall()]
    except Exception:
        return []


def get_current_database_context(client_id: str | None = None) -> dict[str, Any]:
    """
    Read all current information from the database for agentTwo.
    Returns clients, client_suitability_profiles, contract_summary, and products.
    If client_id is provided, contract_summary can be filtered (by owner match).
    """
    clients = get_all_clients()
    profiles = get_all_client_suitability_profiles()
    contracts = get_contract_summary(client_id)
    products = get_all_products()
    return {
        "clients": clients,
        "client_suitability_profiles": profiles,
        "contract_summary": contracts,
        "products": products,
    }
