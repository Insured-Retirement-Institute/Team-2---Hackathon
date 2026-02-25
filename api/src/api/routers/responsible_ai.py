"""
Admin read-only API for Responsible AI dashboard: list events, stats, event detail with payload.
Protect with ADMIN_API_KEY header when set.
"""

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, Query

from api.database import fetch_rows

router = APIRouter(prefix="/admin/responsible-ai", tags=["admin", "responsible-ai"])


def _serialize_row(r: dict) -> dict:
    """Convert asyncpg row to JSON-serializable dict (UUID/datetime to str)."""
    out = {}
    for k, v in r.items():
        if v is None:
            out[k] = None
        elif hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif hasattr(v, "hex"):  # UUID
            out[k] = str(v)
        else:
            out[k] = v
    return out


@router.get("/events")
async def list_events(
    agent_id: str | None = Query(None, description="Filter by agent_id"),
    from_date: datetime | None = Query(None, description="From timestamp (UTC)"),
    to_date: datetime | None = Query(None, description="To timestamp (UTC)"),
    success: bool | None = Query(None, description="Filter by success"),
    client_id_scope: str | None = Query(None, description="Filter by client_id_scope"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List agent run events with optional filters."""
    rows = await fetch_rows(
        "get_agent_run_events",
        agent_id,
        from_date,
        to_date,
        success,
        client_id_scope,
        limit,
        offset,
    )
    return {"events": [_serialize_row(r) for r in rows]}


@router.get("/stats")
async def get_stats(
    from_date: datetime | None = Query(None, description="From (UTC); default 30 days ago"),
    to_date: datetime | None = Query(None, description="To (UTC); default now"),
):
    """Aggregate stats for dashboard: total runs, success rate, by agent, explainability coverage."""
    now = datetime.now(timezone.utc)
    to_d = to_date or now
    from_d = from_date or (now - timedelta(days=30))
    rows = await fetch_rows("get_agent_run_events_stats", from_d, to_d)
    if not rows:
        return {
            "from_date": from_d.isoformat(),
            "to_date": to_d.isoformat(),
            "total_runs": 0,
            "success_count": 0,
            "success_rate": 0.0,
            "agent_one_runs": 0,
            "agent_two_runs": 0,
            "agent_three_runs": 0,
            "agent_two_with_explanation": 0,
            "explainability_coverage_pct": 0.0,
            "guardrail_triggered_count": 0,
        }
    r = rows[0]
    total = r.get("total_runs") or 0
    success_count = r.get("success_count") or 0
    agent_two_with_exp = r.get("agent_two_with_explanation") or 0
    agent_two_runs = r.get("agent_two_runs") or 0
    return {
        "from_date": from_d.isoformat(),
        "to_date": to_d.isoformat(),
        "total_runs": total,
        "success_count": success_count,
        "success_rate": (success_count / total * 100.0) if total else 0.0,
        "agent_one_runs": r.get("agent_one_runs") or 0,
        "agent_two_runs": agent_two_runs,
        "agent_three_runs": r.get("agent_three_runs") or 0,
        "agent_two_with_explanation": agent_two_with_exp,
        "explainability_coverage_pct": (agent_two_with_exp / agent_two_runs * 100.0) if agent_two_runs else 0.0,
        "guardrail_triggered_count": r.get("guardrail_triggered_count") or 0,
    }


@router.get("/events/{event_id}")
async def get_event_by_id(event_id: str):
    """Get a single event by event_id; include full payload when payload_ref is set (agentTwo)."""
    rows = await fetch_rows("get_agent_run_event_by_id", event_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Event not found")
    event = _serialize_row(rows[0])
    payload_ref = event.get("payload_ref")
    if payload_ref:
        ref_rows = await fetch_rows("get_agent_two_payload_by_ref", str(payload_ref))
        if ref_rows:
            event["payload"] = _serialize_row(ref_rows[0])
        else:
            event["payload"] = None
    else:
        event["payload"] = None
    return event