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

## Config

- **SUREIFY_BASE_URL** / **SUREIFY_API_KEY**: When set, the client calls the real Sureify API instead of mock data.
- **SUREIFY_AGENT_TOOL_ONLY**: Set to `1` to skip the LLM and only run the composite tool (see above).
- **SUREIFY_AGENT_SCHEMA_ONLY**: Set to `1` to print the book-of-business JSON schema and exit (no Bedrock).
- Models: Policy shapes come from `api/src/api/sureify_models.py` in this repo.

See [.env.example](../.env.example) for placeholders.

## Layout

- `main.py` – Strands agent, system prompt, and tools (`get_book_of_business`, `get_notifications_for_policies`, `get_book_of_business_with_notifications_and_flags`).
- `sureify_client.py` – Sureify API client (mock when `SUREIFY_BASE_URL` is unset).
- `logic.py` – Business rules: replacement opportunity, data quality, income activation, schedule meeting.
- `schemas.py` – `PolicyOutput`, `BookOfBusinessOutput` (Pydantic) for the frontend.
