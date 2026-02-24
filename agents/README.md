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

- **SUREIFY_BASE_URL** / **SUREIFY_API_KEY**: When set, the client calls the real Sureify API instead of mock data.
- **IRI_API_BASE_URL**: When set, all IRI tools (alerts, alert detail, snooze, dismiss, dashboard, compare, client profile, suitability, disclosures, transaction) call the live API (OpenAPI 1.1.0).
- **SUREIFY_AGENT_TOOL_ONLY**: Set to `1` to skip the LLM and only run the composite tool (see above).
- **SUREIFY_AGENT_IRI_ONLY**: Set to `1` to print IRI alerts + dashboardStats for Marty McFly and exit (no Bedrock).
- **SUREIFY_AGENT_SCHEMA_ONLY**: Set to `1` to print the book-of-business JSON schema and exit (no Bedrock).
- Models: Policy shapes come from `api/src/api/sureify_models.py` in this repo.

See [.env.example](../.env.example) for placeholders.

## Layout

- `main.py` – Strands agent, system prompt, and tools (book of business, JSON schema, IRI alerts and API).
- `sureify_client.py` – Sureify API client (mock when `SUREIFY_BASE_URL` is unset).
- `logic.py` – Business rules: replacement opportunity, data quality, income activation, schedule meeting.
- `schemas.py` – `PolicyOutput`, `BookOfBusinessOutput` (Pydantic) for the frontend.
- `iri_api_spec.yaml` – **OpenAPI 3.0.3** (source of truth for IRI API and DB schema).
- `iri_schemas.py` – **Generated** from the OpenAPI spec (RenewalAlert, DashboardStats, Error, enums). Regenerate with `python -m agents.regenerate_iri_schemas`.
- `iri_client.py` – IRI API HTTP client and mapping from book-of-business to RenewalAlert + DashboardStats.
- `regenerate_iri_schemas.py` – Regenerates `iri_schemas.py` from `iri_api_spec.yaml`.
