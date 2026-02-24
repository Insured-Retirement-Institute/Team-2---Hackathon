# API

FastAPI application for interacting with Sureify CoreCONNECT Edge API.

## Setup

```bash
cd api
uv sync
```

Ensure your `mise.local.toml` has the Sureify credentials:

```toml
SUREIFY_BASE_URL="https://hackathon-dev-api.sureify.com"
SUREIFY_TOKEN_URL="https://hackathon-dev-sureify.auth.us-west-2.amazoncognito.com/oauth2/token"
SUREIFY_CLIENT_ID="your_client_id"
SUREIFY_CLIENT_SECRET="your_client_secret"
SUREIFY_SCOPE="hackathon-dev-EdgeApiM2M/edge"
```

## Sureify Client

### Async Usage

```python
from api.sureify_client import SureifyClient, SureifyAuthConfig
from api.sureify_models import Persona

config = SureifyAuthConfig()  # reads from env vars

async with SureifyClient(config) as client:
    await client.authenticate()

    # Get policies for a user
    policies = await client.get_policies(user_id="1003", persona=Persona.agent)

    # Get cases
    cases = await client.get_cases(user_id="1003", persona=Persona.agent)

    # Get commissions
    commissions = await client.get_commissions(user_id="1003")
```

### Sync Wrapper Functions

```python
import asyncio
from api.sureify_client import (
    SureifyClient,
    SureifyAuthConfig,
    get_policies,
    get_cases,
    get_commissions,
)
from api.sureify_models import Persona

config = SureifyAuthConfig()
client = SureifyClient(config)
asyncio.run(client.authenticate())

policies = get_policies(client, user_id="1003", persona=Persona.agent)
cases = get_cases(client, user_id="1003", persona=Persona.agent)
```

### Available Endpoints

| Method | Return Type | Endpoint |
|--------|-------------|----------|
| `get_applications()` | `list[Application]` | `/puddle/applications` |
| `get_cases()` | `list[Case]` | `/puddle/cases` |
| `get_commissions()` | `list[Commission]` | `/puddle/commissions` |
| `get_commission_statements()` | `list[CommissionStatement]` | `/puddle/commissionStatements` |
| `get_contacts()` | `list[Contact]` | `/puddle/contacts` |
| `get_documents()` | `list[Document]` | `/puddle/documents` |
| `get_document_by_id(id)` | `bytes` | `/puddle/documents/{id}` |
| `get_financial_activities()` | `list[FinancialActivity]` | `/puddle/financialActivities` |
| `get_fund_allocations()` | `list[FundAllocation]` | `/puddle/fundAllocations` |
| `get_keycards()` | `list[Keycard]` | `/puddle/keycards` |
| `get_notes()` | `list[Note]` | `/puddle/notes` |
| `get_payment_methods()` | `list[dict]` | `/puddle/paymentMethods` |
| `get_policies()` | `list[Policy]` | `/puddle/policies` |
| `get_products()` | `list[Product]` | `/puddle/products` |
| `get_qualifications()` | `list[dict]` | `/puddle/qualifications` |
| `get_quotes()` | `list[QuoteIllustrationBase]` | `/puddle/quotes` |
| `get_requirements()` | `list[Requirement]` | `/puddle/requirements` |
| `get_riders()` | `list[Rider]` | `/puddle/riders` |
| `get_roles()` | `list[dict]` | `/puddle/roles` |
| `get_profiles()` | `list[dict]` | `/puddle/profiles` |
| `get_users()` | `list[User]` | `/puddle/users` |

### Common Parameters

All endpoint methods accept these optional parameters:

- `user_id: str` - User ID for authorization (sent as `UserID` header)
- `persona: Persona` - Filter by persona (`Persona.agent` or `Persona.policyowner`)
- `keycard: str` - Keycard identifier for access control

## Running the Server

```bash
uv run uvicorn api.main:app --reload
```
