# Testing Responsible AI

## Automated tests (no database required)

From the **repo root** (with `PYTHONPATH=.` if needed):

```bash
# Agent layer: schemas + audit writer (no DB)
python -m pytest agents/tests/test_responsible_ai.py -v

# Agent behavior: agent_one schema/tool-only, agent_two tools + recommendations, agent_three run_chat (mocked LLM)
python -m pytest agents/tests/test_agents_work.py -v

# Admin API: stats, events list, event by id (mocked DB)
python -m pytest api/tests/test_responsible_ai.py -v

# All agent + Responsible AI tests
python -m pytest agents/tests/ api/tests/test_responsible_ai.py -v
```

- **agents/tests/test_responsible_ai.py:** `AgentRunEvent` build/serialize, `persist_event` / `persist_agent_two_payload` return `False`/`None` when `DATABASE_URL` is unset (no crash).
- **agents/tests/test_agents_work.py:** Agent one schema-only and tool-only paths run and emit events; agent two `get_current_database_context` and `generate_product_recommendations` return valid JSON; agent three `run_chat` builds the message, returns `ChatResponse`, and persists success/failure events (with mocked Strands agent).
- **api/tests/test_responsible_ai.py:** Admin endpoints return the expected JSON shape with mocked `fetch_rows` (empty or sample rows).

## Running agents from the CLI

Use the package entrypoint so the correct module runs (avoids RuntimeWarning):

```bash
# Agent one (schema only, or tool-only, or full run)
PYTHONPATH=. SUREIFY_AGENT_SCHEMA_ONLY=1 python -m agents.agent_one
PYTHONPATH=. SUREIFY_AGENT_TOOL_ONLY=1 python -m agents.agent_one

# Agent two (tool-only = no LLM; or full agent)
PYTHONPATH=. python -m agents.agent_two --tool-only --client-id "Marty McFly"
PYTHONPATH=. python -m agents.agent_two --tool-only --changes /path/to/changes.json --client-id "Marty McFly"

# Agent three (requires Bedrock/LLM credentials for full chat)
PYTHONPATH=. python -m agents.agent_three --screen elsewhere --message "What can you help me with?"
```

## Full flow (with database)

1. **Apply DB schema**  
   Run `database/main.sql` (or at least `agent_two_recommendation_runs.sql` then `agent_run_events.sql`) so the tables exist.

2. **Set `DATABASE_URL`** (or RDS* vars) for both the API and the process that runs the agents.

3. **Run an agent** so it emits events, e.g.:
   ```bash
   PYTHONPATH=. python -m agents.agent_three --screen elsewhere --message "Hello"
   ```
   or run agent_one / agent_two; each run should write one row to `agent_run_events` (and agent_two may also write to `agent_two_recommendation_runs`).

4. **Start the API** and hit the admin endpoints:
   ```bash
   cd api && uvicorn api.main:app --reload
   # Then:
   curl http://localhost:8000/admin/responsible-ai/stats
   curl "http://localhost:8000/admin/responsible-ai/events?limit=5"
   ```

5. **Open the dashboard** at `http://localhost:5173/admin/responsible-ai` (with the frontend dev server and `VITE_API_BASE_URL` pointing at the API). You should see overview cards, by-agent stats, and the event list.

## UUID serialization

The API serializes `event_id` and `payload_ref` (UUIDs) to strings in JSON so the frontend and export stay consistent.
