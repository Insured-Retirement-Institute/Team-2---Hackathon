# AI Inforce Management

## Topic

**AI Inforce Management - Team 2**

## Issue

Managing in-force annuities is fragmented, manual, and compliance-heavy.

- Advisors pull data from multiple carrier systems and formats, creating inefficiency.
- Missed opportunities for replacements, reallocations, or income elections lead to suboptimal client outcomes.
- Compliance reviews and documentation are inconsistent, increasing regulatory risk.
- Carriers face high service volume and manual validation effort.

## Measures of Success

- **Unified advisor dashboard** to view opportunities and take action.
- **50% reduction** in time to identify opportunities.
- **30% reduction** in carrier service interactions through automated processing.

---

## AWS Hackathon sandbox

- **Workshop dashboard:** [AWS Workshop Studio](https://catalog.us-east-1.prod.workshops.aws/event/dashboard/en-US)
- **Bedrock (temp account):** Set the bearer token in your environment so it’s never committed:

  ```bash
  export AWS_BEARER_TOKEN_BEDROCK=<your-token>
  ```

  Or copy `.env.example` to `.env`, add your token there, and load it (e.g. `source .env` or use a dotenv loader). The repo ignores `.env`.

- **RDS PostgreSQL:** Host is in `.env` as `RDSHOST`. To connect:
  1. Add your DB password to `.env` as `RDS_PASSWORD=` (get it from the workshop dashboard).
  2. Run `./connect-db.sh` from the repo root (uses `certs/global-bundle.pem` for SSL).

  Or connect manually:
  ```bash
  source .env
  psql "host=$RDSHOST port=5432 dbname=postgres user=app_user sslmode=verify-full sslrootcert=$(pwd)/certs/global-bundle.pem"
  ```
  (You’ll be prompted for the password if `RDS_PASSWORD` isn’t set.)

- **Database in Cursor:** Install the **SQLTools** and **SQLTools PostgreSQL/Cockroach Driver** extensions. A connection “Team 2 RDS (PostgreSQL)” is in `.vscode/settings.json`. Open the SQLTools sidebar, connect, and enter your DB password when prompted. You can then browse tables and run queries from the editor.

## Get started

### Agents (Sureify book of business)

The **agents** package provides a Strands-based agent that produces the book of business for a customer (e.g. Marty McFly): policies as JSON (using [api/src/api/sureify_models.py](api/src/api/sureify_models.py)), notifications, and flags for replacements, data quality, income activation, and scheduled meetings. Run without an LLM (tool-only, mock data):

```bash
SUREIFY_AGENT_TOOL_ONLY=1 PYTHONPATH=. python -m agents.main
```

See [agents/README.md](agents/README.md) for full agent (Bedrock) and config (Sureify API URL/key).

---

This repository supports the **AI Inforce Management** initiative. We are currently in the process of standing up [SwaggerHub](https://wwww.swaggerhub.com) to host OpenAPI definitions for unified advisor dashboards, carrier data integration, and opportunity identification. More to come.

Please refer to the [style guide](https://github.com/Insured-Retirement-Institute/Style-Guide) for technical governance of standards, data dictionary, and the code of conduct.

## Business Case

In-force annuity management today is fragmented, manual, and compliance-heavy. Advisors pull data from multiple carrier systems and formats, leading to inefficiency, missed opportunities (replacements, reallocations, income elections), and suboptimal client outcomes. Inconsistent compliance reviews and documentation increase regulatory risk, and carriers bear high service volume and manual validation effort.

A unified, AI-enabled approach addresses these issues by providing a single advisor dashboard to view opportunities and take action, targeting a **50% reduction** in time to identify opportunities and a **30% reduction** in carrier service interactions through automated processing. This specification defines the technical and governance foundations to achieve those measures of success.

## User Stories, personna - supporting documents for the business case

**Personas**

- **Advisor:** Financial professional who manages in-force annuities across multiple carriers and needs a single place to see opportunities and act on them without manual data gathering.
- **Carrier:** Insurer or product provider that wants to reduce service volume and manual validation while maintaining compliance and supporting advisor effectiveness.

**User stories**

- As an advisor, I want a unified dashboard so that I can view replacement, reallocation, and income-election opportunities across carriers in one place.
- As an advisor, I want to take action from that dashboard so that I can serve clients better without switching systems or formats.
- As an advisor, I want automated, consistent compliance documentation so that my reviews are thorough and my regulatory risk is lower.
- As a carrier, I want automated processing and validation so that service interactions and manual effort are reduced while remaining compliant.
- As a carrier, I want normalized data and clear APIs so that advisors can integrate our in-force data into their workflow efficiently.

## Business Owners

- Carrier Business Owner: contact
- Distributor Business Owner: contact
- Solution Provider Business Owner: contact

## How to engage, contribute, and give feedback

- Working groups for **AI Inforce Management** (unified dashboard, opportunity identification, carrier integration) are being scheduled. Please contact the business owners or IRI (hpikus@irionline.org) to get added to the working group discussions.

## Change subsmissions and reporting issues and bugs

Security issues and bugs should be reported directly to Katherine Dease kdease@irionline.org. Issues and bugs can be reported directly within the issues tab of a repository. Change requests should follow the standards governance workflow outlined on the [main page](https://github.com/Insured-Retirement-Institute).

## Code of conduct

See [style guide](https://github.com/Insured-Retirement-Institute/Style-Guide)
