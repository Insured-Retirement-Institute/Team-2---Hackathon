"""
Sync database writer for responsible-AI agent run events. Writes to agent_run_events,
agent_two_recommendation_runs, and client_suitability_profiles. Uses DATABASE_URL or RDS* env vars.
Same connection pattern as agents/db_reader.py.
"""

from __future__ import annotations

import os
import uuid
from typing import Any

import psycopg2
from psycopg2.extras import Json


from agents.logging_config import get_logger
from agents.agent_two_schemas import ProfileChangesInput
from agents.responsible_ai_schemas import AgentRunEvent

logger = get_logger(__name__)


def _get_connection_params() -> dict[str, Any] | None:
    url = os.environ.get("DATABASE_URL")
    if url and url.strip() and url != "postgresql://":
        return {"dsn": url}
    # Prefer libpq-style PG* (so all agents + API can share env)
    host = os.environ.get("PGHOST") or os.environ.get("RDSHOST")
    user = os.environ.get("PGUSER") or os.environ.get("RDS_USER")
    password = os.environ.get("PGPASSWORD") or os.environ.get("RDS_PASSWORD")
    dbname = os.environ.get("PGDATABASE") or os.environ.get("RDS_DB", "postgres")
    port_str = os.environ.get("PGPORT") or os.environ.get("RDS_PORT", "5432")
    if host and user and password:
        try:
            port = int(port_str)
        except ValueError:
            port = 5432
        return {
            "host": host,
            "user": user,
            "password": password,
            "dbname": dbname,
            "port": port,
        }
    return None


def persist_event(event: AgentRunEvent) -> bool:
    """
    Insert one AgentRunEvent into agent_run_events. Returns True if written, False if DB
    not configured or on error (logged).
    """
    params = _get_connection_params()
    if not params or psycopg2 is None or Json is None:
        return False
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO hackathon.agent_run_events (
                        event_id, timestamp, agent_id, run_id, client_id_scope,
                        input_summary, success, error_message, explanation_summary,
                        data_sources_used, choice_criteria, input_validation_passed,
                        guardrail_triggered, payload_ref
                    ) VALUES (
                        %s, %s::timestamptz, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        event.event_id,
                        event.timestamp,
                        event.agent_id.value,
                        event.run_id,
                        event.client_id_scope,
                        Json(event.input_summary),
                        event.success,
                        event.error_message,
                        event.explanation_summary,
                        event.data_sources_used,
                        event.choice_criteria,
                        event.input_validation_passed,
                        event.guardrail_triggered,
                        uuid.UUID(event.payload_ref) if event.payload_ref else None,
                    ),
                )
            conn.commit()
        return True
    except Exception as e:
        logger.warning("audit_writer: failed to persist event %s: %s", event.event_id, e)
        return False


def persist_agent_one_book_of_business(
    run_id: str,
    created_at: str,
    customer_identifier: str,
    payload: dict,
) -> str | None:
    """
    Insert agent one's book-of-business JSON (policies with notifications and flags) into agent_one_book_of_business.
    Returns the inserted row id (UUID string), or None on error or when DB is not configured.
    """
    params = _get_connection_params()
    if not params or psycopg2 is None or Json is None:
        return None
    row_id = str(uuid.uuid4())
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO hackathon.agent_one_book_of_business (id, run_id, created_at, customer_identifier, payload)
                    VALUES (%s::uuid, %s, %s::timestamptz, %s, %s)
                    """,
                    (row_id, run_id, created_at, customer_identifier, Json(payload)),
                )
            conn.commit()
        return row_id
    except Exception as e:
        logger.warning(
            "audit_writer: failed to persist agent_one book_of_business run_id=%s: %s",
            run_id,
            e,
        )
        return None


def persist_agent_two_payload(
    run_id: str,
    created_at: str,
    client_id: str,
    payload: dict,
) -> str | None:
    """
    Insert a full agentTwo storable payload into agent_two_recommendation_runs.
    Returns the inserted row id (UUID string) for use as payload_ref, or None on error.
    """
    params = _get_connection_params()
    if not params or psycopg2 is None or Json is None:
        return None
    row_id = str(uuid.uuid4())
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO hackathon.agent_two_recommendation_runs (id, run_id, created_at, client_id, payload)
                    VALUES (%s::uuid, %s, %s::timestamptz, %s, %s)
                    """,
                    (row_id, run_id, created_at, client_id, Json(payload)),
                )
            conn.commit()
        return row_id
    except Exception as e:
        logger.warning("audit_writer: failed to persist agent_two payload run_id=%s: %s", run_id, e)
        return None


# ---- client_suitability_profiles: columns (must match database/client_suitability_profiles.sql) ----
_PROFILE_COLUMNS = [
    "client_account_number",
    "age",
    "life_stage",
    "marital_status",
    "dependents",
    "risk_tolerance",
    "investment_experience",
    "volatility_comfort",
    "primary_objective",
    "secondary_objective",
    "liquidity_importance",
    "investment_horizon",
    "withdrawal_horizon",
    "current_income_need",
    "annual_income_range",
    "net_worth_range",
    "liquid_net_worth_range",
    "tax_bracket",
    "retirement_target_year",
    "state",
    "citizenship",
    "advisory_model",
    "is_fee_based_account",
]


def build_profile_row_from_changes(
    client_account_number: str,
    changes: ProfileChangesInput,
    existing_row: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Build a row dict for client_suitability_profiles from front-end changes and optional existing DB row.
    Keys are DB column names. Only includes fields we can set from changes or existing row.
    """
    row: dict[str, Any] = {"client_account_number": client_account_number}

    # Start from existing row (excluding key)
    if existing_row:
        for c in _PROFILE_COLUMNS:
            if c == "client_account_number":
                continue
            if existing_row.get(c) is not None:
                row[c] = existing_row[c]

    # Override / set from suitability changes
    if changes.suitability:
        s = changes.suitability
        if s.riskTolerance is not None:
            row["risk_tolerance"] = s.riskTolerance
        if s.timeHorizon is not None:
            row["investment_horizon"] = s.timeHorizon
        if s.liquidityNeeds is not None:
            row["liquidity_importance"] = s.liquidityNeeds
        if s.clientObjectives is not None:
            row["primary_objective"] = s.clientObjectives

    # Override / set from client_profile changes
    if changes.client_profile:
        p = changes.client_profile
        if p.taxBracket is not None:
            row["tax_bracket"] = p.taxBracket
        if p.householdNetWorth is not None:
            row["net_worth_range"] = p.householdNetWorth
        if p.householdLiquidAssets is not None:
            row["liquid_net_worth_range"] = p.householdLiquidAssets
        if p.grossIncome is not None:
            row["annual_income_range"] = p.grossIncome

    return row


def upsert_client_suitability_profile(
    client_account_number: str,
    profile_dict: dict[str, Any],
) -> bool:
    """
    Insert or update one row in client_suitability_profiles.
    profile_dict must include client_account_number and any columns to set (DB column names).
    Returns True if written, False if DB not configured or on error.
    """
    params = _get_connection_params()
    if not params or psycopg2 is None:
        return False

    # Only include columns that exist in the table and have values
    allowed = set(_PROFILE_COLUMNS)
    cols = [k for k in profile_dict if k in allowed and profile_dict[k] is not None]
    if not cols or "client_account_number" not in cols:
        return False

    values = [profile_dict[k] for k in cols]
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    # On conflict update all provided columns except the key
    update_set = ", ".join(
        f"{c} = EXCLUDED.{c}" for c in cols if c != "client_account_number"
    )

    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO hackathon.client_suitability_profiles ({col_list})
                    VALUES ({placeholders})
                    ON CONFLICT (client_account_number)
                    DO UPDATE SET {update_set}
                    """,
                    values,
                )
            conn.commit()
        return True
    except Exception as e:
        logger.warning(
            "audit_writer: failed to upsert client_suitability_profile client=%s: %s",
            client_account_number,
            e,
        )
        return False
