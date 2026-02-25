# Payload schemas for DBAs

This folder contains YAML definitions of **payloads** produced and consumed by the agents and APIs. Use them to:

- Design or validate database tables (staging, persistence, ETL)
- Map API/agent JSON to existing tables (`clients`, `client_suitability_profiles`, `contract_summary`, `products`)
- Understand required vs optional fields and types

| File | Contents |
|------|----------|
| **agent_one_payload.yaml** | Book-of-business output (AgentOne): customer identifier + policies with notifications and flags |
| **agent_two_payloads.yaml** | AgentTwo: DB context payload, profile-changes input, product-recommendations output |
| **agent_two_storable_payload.yaml** | AgentTwo **storable payload**: run_id, created_at, client_id, **explanation** (choices), recommendations; use for table design to persist recommendation runs |
| **agent_two_recommendation_runs_table.yaml** | **Table spec for DBAs:** agent_two_recommendation_runs (id, run_id, created_at, client_id, payload JSONB). References agent_two_storable_payload.yaml for payload schema. DDL: `../agent_two_recommendation_runs.sql`. |
| **agent_three_chat_payloads.yaml** | AgentThree (chatbot): ChatRequest (screen_state, user_message, client_id, changes_json, alert_id) and ChatResponse (reply, screen_state, agent_two_invoked, storable_payload) |
| **responsible_ai_agent_run_events.yaml** | **Responsible AI — table spec for DBAs:** agent_run_events (unified audit events from all three agents). Columns, indexes, FK to agent_two_recommendation_runs. Event schema (AgentRunEvent) included. DDL: `../agent_run_events.sql`. |

**Related:**

- Table DDL: `../*.sql` (e.g. `../agent_run_events.sql`, `../agent_two_recommendation_runs.sql`)
- IRI API (camelCase, OpenAPI): `../../agents/iri_api_spec.yaml`
