"""
Sync database writer for responsible-AI agent run events. Writes to agent_run_events
and (for agentTwo) to agent_two_recommendation_runs. Uses DATABASE_URL or RDS* env vars.
Same connection pattern as agents/db_reader.py.
"""

from __future__ import annotations

import os
import uuid

try:
    import psycopg2
    from psycopg2.extras import Json
except ImportError:
    psycopg2 = None  # type: ignore
    Json = None  # type: ignore

from agents.logging_config import get_logger
from agents.responsible_ai_schemas import AgentRunEvent

logger = get_logger(__name__)


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
                    INSERT INTO agent_run_events (
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
                    INSERT INTO agent_two_recommendation_runs (id, run_id, created_at, client_id, payload)
                    VALUES (%s::uuid, %s, %s::timestamptz, %s, %s)
                    """,
                    (row_id, run_id, created_at, client_id, Json(payload)),
                )
            conn.commit()
        return row_id
    except Exception as e:
        logger.warning("audit_writer: failed to persist agent_two payload run_id=%s: %s", run_id, e)
        return None
