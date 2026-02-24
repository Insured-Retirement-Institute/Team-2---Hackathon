# Sureify Book of Business Agent

Strands-based agent that scans Sureify APIs and produces the **book of business** for a customer (e.g. **Marty McFly**), with all policies as JSON (aligned with [api/src/api/sureify_models.py](../api/src/api/sureify_models.py)), applicable notifications, and business-logic flags: replacements, data quality issues, income activation eligibility, and scheduled-meeting recommendation.

## Quick start (tool-only, no LLM)

Runs the composite tool only (mock Sureify data, no Bedrock/credentials):

```bash
# From repo root
SUREIFY_AGENT_TOOL_ONLY=1 PYTHONPATH=. python -m agents.main
```

Output: single JSON object with `customer_identifier` and `policies` array; each policy includes `policy`, `notifications`, `replacement_opportunity`, `replacement_reason`, `data_quality_issues`, `income_activation_eligible`, `schedule_meeting`, `schedule_meeting_reason`.

## Full agent (Strands + LLM)

Requires Bedrock with **native IAM auth**. Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` in `.env` (or use `aws configure`). `.env` is loaded automatically; bearer token is not used.

```bash
PYTHONPATH=. python -m agents.main
```

The agent will use the tools to produce the same book-of-business JSON for Marty McFly.

## JSON schema for database team

To get a JSON schema describing the book-of-business structure (for your DB admin team to build tables):

- **Via agent:** Run the agent and ask: *"Create a JSON schema I can share with my database admin team to build the table."* The agent will call `get_book_of_business_json_schema` and return the schema.
- **Direct (no LLM):**  
  `SUREIFY_AGENT_SCHEMA_ONLY=1 PYTHONPATH=. python -m agents.main`  
  Pipe to a file to share: `... > book_of_business_schema.json`

## IRI API (renewal alerts + dashboard) — OpenAPI-driven

The **OpenAPI spec** [agents/iri_api_spec.yaml](iri_api_spec.yaml) is the **source of truth** for the IRI API and for database design. Pydantic models in `iri_schemas.py` are generated from the spec; regenerate after editing the spec:

```bash
pip install 'datamodel-code-generator[http]'
PYTHONPATH=. python -m agents.regenerate_iri_schemas
```

- **IRI-shaped output from book of business:** Use tool `get_book_of_business_as_iri_alerts` (or run with `SUREIFY_AGENT_IRI_ONLY=1`) to get `alerts` (RenewalAlert[]) and `dashboardStats` derived from Sureify + agent logic. No live IRI server required.
- **Live IRI API (spec 1.1.0):** When `IRI_API_BASE_URL` is set, the agent can call Dashboard (`get_iri_alerts`, `get_iri_alert_by_id` → AlertDetail, `get_iri_dashboard_stats`), Alert Actions (`snooze_iri_alert`, `dismiss_iri_alert`), Compare (`run_iri_comparison`, `get_iri_client_profile`, `save_iri_client_profile`), and Action tab (`save_iri_suitability`, `save_iri_disclosures`, `submit_iri_transaction`).

```bash
# Output book of business as IRI alerts + dashboardStats (no LLM)
SUREIFY_AGENT_IRI_ONLY=1 PYTHONPATH=. python -m agents.main
```

## Config

- **Sureify (book of business):** AgentOne uses the same client as the API ([api.sureify_client](../api/src/api/sureify_client.py)). Set **SUREIFY_BASE_URL**, **SUREIFY_CLIENT_ID**, and **SUREIFY_CLIENT_SECRET** to call `get_policies` and `get_notes`; when unset, the agent uses mock data for Marty McFly.
- **IRI_API_BASE_URL**: When set, all IRI tools (alerts, alert detail, snooze, dismiss, dashboard, compare, client profile, suitability, disclosures, transaction) call the live API (OpenAPI 1.1.0).
- **SUREIFY_AGENT_TOOL_ONLY**: Set to `1` to skip the LLM and only run the composite tool (see above).
- **SUREIFY_AGENT_IRI_ONLY**: Set to `1` to print IRI alerts + dashboardStats for Marty McFly and exit (no Bedrock).
- **SUREIFY_AGENT_SCHEMA_ONLY**: Set to `1` to print the book-of-business JSON schema and exit (no Bedrock).
- Models: Policy shapes come from `api/src/api/sureify_models.py` in this repo.

See [.env.example](../.env.example) for placeholders.

## AgentTwo (DB + changes → product recommendations)

**AgentTwo** reads the database for current information (clients, suitability profiles, contracts, products), accepts JSON from the front-end with **changes to suitability, client goals, or client profile**, and generates **new product recommendations**.

```bash
# Tool-only (no LLM): dump DB context, then recommendations if --changes provided
PYTHONPATH=. python -m agents.agent_two --tool-only --client-id "Marty McFly"
PYTHONPATH=. python -m agents.agent_two --tool-only --changes changes.json --client-id "Marty McFly"

# Full agent (Strands + LLM)
PYTHONPATH=. python -m agents.agent_two
PYTHONPATH=. python -m agents.agent_two --changes changes.json --client-id "Marty McFly" --alert-id "alert-123"
```

- **Database:** Set `DATABASE_URL` or `RDSHOST` + `RDS_USER` + `RDS_PASSWORD` (optional `RDS_DB`). AgentTwo uses sync reads via `agents/db_reader.py`.
- **Changes JSON:** Optional keys `suitability`, `clientGoals`, `clientProfile` (each with optional fields). Only include what changed; agentTwo merges with DB state.
- **IRI:** If `IRI_API_BASE_URL` and `--alert-id` are set, agentTwo can save profile/suitability to IRI and run comparison, then include that in the result.

See `agents/agent_two_schemas.py` for `ProfileChangesInput` and `ProductRecommendationsOutput` shapes.

### How to test agentTwo

**1. Install and set env (from repo root)**

```bash
uv sync
# Optional: copy .env.example to .env and set DB (for real data):
# DATABASE_URL=postgresql://user:pass@host/dbname
# or RDSHOST, RDS_USER, RDS_PASSWORD
```

**2. Tool-only (no LLM, no Bedrock)** — good for quick checks

```bash
# Dump current DB context (clients, suitability profiles, contracts, products)
PYTHONPATH=. python -m agents.agent_two --tool-only --client-id "Marty McFly"

# Same + run recommendations using sample changes
PYTHONPATH=. python -m agents.agent_two --tool-only --changes agents/sample_changes.json --client-id "Marty McFly"
```

If the DB isn’t configured, `clients` / `client_suitability_profiles` / `contract_summary` / `products` will be empty and recommendations will be empty. Set `DATABASE_URL` or RDS vars and ensure the tables exist to see data.

**3. Full agent (Strands + LLM)** — needs Bedrock/AWS credentials in `.env`

```bash
PYTHONPATH=. python -m agents.agent_two --client-id "Marty McFly"
PYTHONPATH=. python -m agents.agent_two --changes agents/sample_changes.json --client-id "Marty McFly"
```

## Layout

- `main.py` – Strands agent (agentOne), system prompt, and tools (book of business, JSON schema, IRI alerts and API).
- `agent_two.py` – AgentTwo: DB context + front-end changes JSON → product recommendations.
- `db_reader.py` – Sync DB reader for agentTwo (clients, client_suitability_profiles, contract_summary, products).
- `agent_two_schemas.py` – `ProfileChangesInput`, `ProductRecommendation`, `ProductRecommendationsOutput`.
- `recommendations.py` – Merge DB + changes and recommend products from the products table.
- `sureify_client.py` – Delegates to [api.sureify_client](../api/src/api/sureify_client.py) when configured (`SUREIFY_BASE_URL` + `SUREIFY_CLIENT_ID` + `SUREIFY_CLIENT_SECRET`); otherwise mock data for Marty McFly. Exposes `get_book_of_business` (→ get_policies) and `get_notifications_for_policies` (→ get_notes).
- `logic.py` – Business rules: replacement opportunity, data quality, income activation, schedule meeting.
- `schemas.py` – `PolicyOutput`, `BookOfBusinessOutput` (Pydantic) for the frontend.
- `iri_api_spec.yaml` – **OpenAPI 3.0.3** (source of truth for IRI API and DB schema).
- `iri_schemas.py` – **Generated** from the OpenAPI spec (RenewalAlert, DashboardStats, Error, enums). Regenerate with `python -m agents.regenerate_iri_schemas`.
- `iri_client.py` – IRI API HTTP client and mapping from book-of-business to RenewalAlert + DashboardStats.
- `regenerate_iri_schemas.py` – Regenerates `iri_schemas.py` from `iri_api_spec.yaml`.
