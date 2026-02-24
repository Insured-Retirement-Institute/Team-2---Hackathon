# Schema and model alignment

## OpenAPI is the source of truth (IRI)

**`iri_api_spec.yaml`** drives the IRI API and database design:

- **Database**: Design tables from the OpenAPI **components/schemas** (RenewalAlert, DashboardStats, Error, AlertType). The spec defines required fields, enums, and types.
- **Pydantic models**: **`iri_schemas.py`** is **generated** from the OpenAPI spec. Do not edit it by hand. After changing the spec, regenerate:
  ```bash
  pip install 'datamodel-code-generator[http]'
  PYTHONPATH=. python -m agents.regenerate_iri_schemas
  ```
- **Agent and client code** use the generated models (RenewalAlert, DashboardStats, AlertType, Priority, Status). Mapping from book-of-business to IRI shape is in `iri_client.map_book_of_business_to_iri_alerts`.

---

## Two output shapes

| Source | Naming | Use |
|--------|--------|-----|
| **Book of business** (`schemas.py`, `agentOneOutputSchema.json`) | **snake_case** | Agent tool output: `customer_identifier`, `policies[]` with `replacement_opportunity`, `data_quality_issues`, etc. |
| **IRI API** (`iri_api_spec.yaml` → `iri_schemas.py`) | **camelCase** | Dashboard/alerts: `RenewalAlert`, `DashboardStats`. Schema comes from OpenAPI. |

The same underlying data can be returned in either shape. Book-of-business → IRI mapping is in `iri_client`.

---

## Book of business (agent output)

- **`schemas.py`** defines Pydantic models; **`agentOneOutputSchema.json`** is generated from `BookOfBusinessOutput.model_json_schema()`.
- **`policy`** is a generic object; inner structure is from Sureify. For DB: use JSONB or a separate policy schema.

---

## IRI (OpenAPI-driven)

- **`iri_api_spec.yaml`**: canonical. **`iri_schemas.py`**: generated from it (AlertType, Priority, Status as enums; RenewalAlert, DashboardStats, Error).
- **DB team**: Build tables from **`iri_api_spec.yaml`** `components/schemas` (or from JSON schema exported from the generated Pydantic models).
