# Database

Database table schemas, managed by pgschema!

## Payloads (for DBAs)

YAML definitions of agent/API payloads for table design and ETL:

- **[payloads/](payloads/)** — `agent_one_payload.yaml` (book of business), `agent_two_payloads.yaml` (DB context, profile changes input, product recommendations output). See [payloads/README.md](payloads/README.md).

## Usage

Preview schema changes:
```bash
mise run pgschema:plan
```

Apply schema changes:
```bash
mise run pgschema:apply
```
