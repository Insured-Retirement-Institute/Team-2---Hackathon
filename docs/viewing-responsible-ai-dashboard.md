# Viewing the Responsible AI Dashboard

The dashboard is at **`/admin/responsible-ai`**. It shows overview stats, by-agent breakdown, and a table of recent run events with a detail modal.

## Quick start (see the UI)

1. **Start the API** (requires Postgres with `agent_run_events` and `agent_two_recommendation_runs`; see `database/main.sql`):
   ```bash
   cd api && uvicorn api.main:app --reload --port 8000
   ```
   If you don’t have a DB, the API may not start. You can still run the frontend; the dashboard will show the layout and toasts when requests fail.

2. **Start the frontend** from the repo root:
   ```bash
   cd frontend && npm run dev
   ```

3. **Open the dashboard** in your browser:
   ```
   http://localhost:5173/admin/responsible-ai
   ```

With the default setup, the frontend proxies **`/api-backend`** to `http://localhost:8000` (so the app route `/admin/responsible-ai` is served by Vite, and only API requests use the proxy). You don’t need to set `VITE_API_BASE_URL` for local dev. If your API runs on another host/port, create `frontend/.env` with:
```env
VITE_API_BASE_URL=http://localhost:8000
```
Then the dashboard will call that base URL for `/admin/responsible-ai/*` (no proxy).

## What you’ll see

- **Overview cards:** Total runs, success rate, explainability coverage (Agent Two), guardrail triggered count.
- **By agent:** Run counts for Agent One, Two, and Three; Agent Two shows runs with explanation.
- **Recent events table:** Timestamp, agent, success, explanation summary, validation, guardrail; **Detail** opens a modal (and for Agent Two, the full payload when `payload_ref` is set).
- **Time range:** Last 7 or 30 days; **All agents** or filter by agent.

To get real data, run the agents (with `DATABASE_URL` set) so they write to `agent_run_events` (and Agent Two to `agent_two_recommendation_runs`), then refresh the dashboard.
