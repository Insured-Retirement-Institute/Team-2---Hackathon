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

**Related:**

- Table DDL: `../tables/*.sql`
- IRI API (camelCase, OpenAPI): `../../agents/iri_api_spec.yaml`
