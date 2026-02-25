# Sureify Book of Business Agent

Strands-based agent that scans Sureify APIs and produces the **book of business** for a customer (e.g. **Marty McFly**), with all policies as JSON (aligned with [api/src/api/sureify_models.py](../api/src/api/sureify_models.py)), applicable notifications, and business-logic flags: replacements, data quality issues, income activation eligibility, and scheduled-meeting recommendation.

## AgentOne — Quick start (tool-only, no LLM)

Runs the composite tool only (mock Sureify data, no Bedrock/credentials):

```bash
# From repo root
SUREIFY_AGENT_TOOL_ONLY=1 PYTHONPATH=. python -m agents.agent_one
```

Output: single JSON object with `customer_identifier` and `policies` array; each policy includes `policy`, `notifications`, `replacement_opportunity`, `replacement_reason`, `data_quality_issues`, `income_activation_eligible`, `schedule_meeting`, `schedule_meeting_reason`.

## AgentOne — Full agent (Strands + LLM)

Requires Bedrock with **native IAM auth**. Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` in `.env` (or use `aws configure`). `.env` is loaded automatically; bearer token is not used.

```bash
PYTHONPATH=. python -m agents.agent_one
```

The agent will use the tools to produce the same book-of-business JSON for Marty McFly.

## AgentOne — JSON schema for database team

To get a JSON schema describing the book-of-business structure (for your DB admin team to build tables):

- **Via agent:** Run the agent and ask: *"Create a JSON schema I can share with my database admin team to build the table."* The agent will call `get_book_of_business_json_schema` and return the schema.
- **Direct (no LLM):**  
  `SUREIFY_AGENT_SCHEMA_ONLY=1 PYTHONPATH=. python -m agents.agent_one`  
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
SUREIFY_AGENT_IRI_ONLY=1 PYTHONPATH=. python -m agents.agent_one
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

## AgentThree (chatbot)

**AgentThree** is the main chatbot. It receives the user's **current screen state** (dashboard, product_comparison, or elsewhere) and uses that as context. When the user asks about **products** or **recommendation explainability** ("why did you recommend this?"), it delegates to **agentTwo** and explains the results in a friendly way.

```bash
# Run chatbot (needs Bedrock/AWS in .env)
PYTHONPATH=. python -m agents.agent_three --screen product_comparison --message "Why did you recommend this product?"
PYTHONPATH=. python -m agents.agent_three --screen dashboard --message "What can you help me with?"
PYTHONPATH=. python -m agents.agent_three --screen elsewhere --message "I want new recommendations" --changes agents/sample_changes.json --client-id "Marty McFly"
```

- **Screen state:** Front-end sends `screen_state`: `dashboard` | `product_comparison` | `elsewhere`. The agent uses it to tailor tone and when to call agentTwo.
- **AgentTwo delegation:** AgentThree has tools `get_recommendation_context(client_id)` and `get_product_recommendations_and_explanation(changes_json, client_id, alert_id)`. It calls them when the user asks for context, recommendations, or explainability.
- **Request/response:** See `agents/agent_three_schemas.py` (`ChatRequest`, `ChatResponse`) and `database/payloads/agent_three_chat_payloads.yaml` for DBA.

## Layout

Agents are in subfolders; shared code stays under `agents/`:

| Path | Description |
|------|--------------|
| **agent_one/** | Book of business (Sureify policies, notifications, IRI). Run: `python -m agents.agent_one` |
| **agent_two/** | DB + changes → product recommendations (explanation, storable payload). Run: `python -m agents.agent_two` |
| **agent_three/** | Chatbot (screen state, delegates to agentTwo). Run: `python -m agents.agent_three` |
| `db_reader.py` | Sync DB reader (clients, client_suitability_profiles, contract_summary, products) |
| `agent_two_schemas.py` | ProfileChangesInput, ProductRecommendationsOutput, AgentTwoStorablePayload, etc. |
| `agent_three_schemas.py` | ScreenState, ChatRequest, ChatResponse |
| `recommendations.py` | Merge DB + changes; recommend from Sureify /puddle/products or DB |
| `sureify_client.py` | get_book_of_business, get_notifications_for_policies, get_products (or mock) |
| `logic.py` | Replacement, data quality, income activation, schedule meeting |
| `schemas.py` | PolicyOutput, BookOfBusinessOutput (frontend) |
| `iri_api_spec.yaml` | OpenAPI 3.0.3 (IRI API); `iri_schemas.py` generated from it |
| `iri_client.py` | IRI HTTP client; map book-of-business → RenewalAlert + DashboardStats |
| `regenerate_iri_schemas.py` | Regenerate `iri_schemas.py` from spec |
| `sample_changes.json` | Sample profile changes for testing agentTwo/agentThree |
