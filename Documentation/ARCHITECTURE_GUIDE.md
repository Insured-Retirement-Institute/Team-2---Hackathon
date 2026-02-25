# Architecture Decision Guide

## One FastAPI App vs Multiple Services

### ✅ Recommendation: ONE FastAPI App (Monolith with Routers)

For your hackathon project, use **one FastAPI application** with multiple routers.

```
┌─────────────────────────────────────────────┐
│        FastAPI App (Port 8000)              │
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │ Alerts       │  │ Clients      │       │
│  │ Router       │  │ Router       │       │
│  │ (Local DB)   │  │ (Fetch&Merge)│       │
│  └──────────────┘  └──────────────┘       │
│                                             │
│  ┌──────────────┐  ┌──────────────┐       │
│  │ Products     │  │ Passthrough  │       │
│  │ Router       │  │ Router       │       │
│  │ (Cached)     │  │ (Proxy)      │       │
│  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────┘
         │                    │
         ↓                    ↓
   PostgreSQL            Sureify API
```

---

## Data Source Patterns

### Pattern 1: Local Database Only ✅ `/api/alerts`

**Use when:** Data is generated/managed by your system

```python
@router.get("/alerts")
async def get_alerts():
    # Read directly from your database
    rows = await fetch_rows("get_alerts")
    return rows
```

**Example endpoints:**
- `GET /api/alerts` - Your generated alerts
- `GET /api/dashboard/stats` - Calculated statistics
- `POST /api/alerts/{id}/snooze` - State changes

**Pros:**
- ⚡ Fast (no network calls)
- 🎯 Full control over data
- 📊 Can add indexes/optimize queries

---

### Pattern 2: Fetch & Merge ✅ `/api/clients/{id}/profile`

**Use when:** Need real-time data + local customizations

```python
@router.get("/clients/{client_id}/profile")
async def get_client_profile(client_id: str, sureify: SureifyClient):
    # 1. Fetch base data from source system
    base = await sureify.get_contact(user_id=client_id)

    # 2. Fetch local overrides
    overrides = await db.fetch_one(
        "SELECT * FROM client_profile_overrides WHERE client_id = $1",
        client_id
    )

    # 3. Merge (local wins)
    return {**base, **overrides}
```

**Example endpoints:**
- `GET /api/clients/{id}/profile` - Sureify data + your notes
- `PUT /api/clients/{id}/profile` - Save local overrides
- `GET /api/policies/{id}/details` - Policy + your annotations

**Pros:**
- 📡 Always fresh source data
- ✏️ Local customizations preserved
- 💾 Minimal storage (only store deltas)

**Cons:**
- 🐌 Slower (network call per request)
- 🔌 Dependent on source API

**When to use:**
- Source data changes frequently
- Need real-time accuracy
- Local overrides are sparse

---

### Pattern 3: Cache with Expiration ✅ `/api/products`

**Use when:** Data rarely changes, high traffic

```python
from datetime import timedelta
from functools import lru_cache

# In-memory cache (15 minutes)
@router.get("/products")
async def get_products():
    cache_key = "products:all"

    # Check cache
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fetch from source
    products = await sureify.get_products(persona=Persona.agent)

    # Cache for 15 minutes
    await cache.setex(cache_key, 900, json.dumps(products))
    return products
```

**Example endpoints:**
- `GET /api/products` - Product catalog (changes rarely)
- `GET /api/carriers` - Carrier list (stable data)
- `GET /api/config` - Application config

**Pros:**
- ⚡⚡⚡ Very fast (cache hits)
- 📉 Reduced load on source API
- 🎯 Works during source downtime

**Cons:**
- 🕐 Data can be stale
- 🧠 Need cache infrastructure (Redis recommended)

**When to use:**
- Data changes infrequently (hours/days)
- High read volume
- Source API is slow or rate-limited

---

### Pattern 4: Direct Proxy ✅ `/passthrough/*`

**Use when:** Admin/debugging access to source API

```python
@router.get("/passthrough/policies")
async def passthrough_policies(sureify: SureifyClient):
    # Direct pass-through to Sureify
    return await sureify.get_policies(user_id="1003", persona=Persona.agent)
```

**Example endpoints:**
- `GET /passthrough/policies` - Raw Sureify data
- `GET /passthrough/contacts` - Unmodified contacts
- For debugging and admin tools only

**Pros:**
- 🔍 Easy debugging
- 📋 No data transformation
- 🎯 See exactly what source returns

**Cons:**
- 🐌 Slow (no cache)
- 🔓 Exposes raw API structure

**When to use:**
- Development/debugging
- Admin panels
- Testing integrations

---

## Recommended Pattern by Endpoint Type

| Endpoint Type | Pattern | Example |
|--------------|---------|---------|
| Your business logic | Local DB | Alerts, notifications |
| Source + your edits | Fetch & Merge | Client profiles, policy notes |
| Rarely changing data | Cache | Product catalog, carriers |
| Admin/debug | Proxy | Raw Sureify access |

---

## Database Schema Strategy

### Store ONLY What You Need

```sql
-- ✅ Good: Store minimal overrides
CREATE TABLE client_profile_overrides (
    client_id varchar PRIMARY KEY,
    risk_tolerance varchar,    -- Your override
    investment_objectives text, -- Your override
    notes text                  -- Your addition
);

-- ❌ Bad: Duplicating all source data
CREATE TABLE clients_full_copy (
    client_id varchar,
    -- ... 50 fields copied from Sureify
);
```

**Why?**
- Minimal storage
- No sync jobs needed
- Clear which data is "yours"
- Source remains source of truth

---

## Scaling Considerations

### When to Split into Microservices

**Stay monolith if:**
- ✅ Team < 10 developers
- ✅ All endpoints have similar traffic
- ✅ Deployment is simple
- ✅ Shared database connections beneficial

**Consider microservices if:**
- ❌ Need to scale specific endpoints independently
- ❌ Different teams own different domains
- ❌ Some services need different languages/tech
- ❌ Deployment frequency varies by domain

**For your hackathon:** Definitely stay monolith.

---

## Deployment Options

### Option 1: Docker + ECS (Recommended)

```dockerfile
# Dockerfile already exists in your repo
FROM python:3.13
COPY api /app/api
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

```bash
# Deploy to AWS ECS
docker build -t hackathon-api .
docker push ecr.amazonaws.com/hackathon-api
# ECS pulls and runs
```

**Pros:**
- Simple container deployment
- Auto-scaling available
- Health checks built-in

---

### Option 2: Docker Compose (Local/Demo)

```bash
# Your repo already has docker-compose.yml
docker-compose up

# Starts:
# - FastAPI backend
# - PostgreSQL database
# - Any other services
```

Perfect for demos and local development.

---

## Performance Tips

### 1. Use Connection Pooling

```python
# Already implemented in api/database.py
pool = await asyncpg.create_pool(DATABASE_URL)
```

Reuses database connections across requests.

### 2. Batch External API Calls

```python
# ❌ Bad: N+1 problem
for client_id in client_ids:
    profile = await sureify.get_contact(user_id=client_id)

# ✅ Good: Batch fetch
profiles = await sureify.get_contacts()  # Get all at once
```

### 3. Add Caching Layer

```python
# Use Redis for shared cache across instances
import redis.asyncio as redis

cache = redis.from_url("redis://localhost")
```

### 4. Use Async Properly

```python
# ✅ Good: Concurrent requests
import asyncio

results = await asyncio.gather(
    sureify.get_policies(),
    db.fetch_alerts(),
    cache.get_products()
)
```

---

## Security Considerations

### 1. Validate External Data

```python
from pydantic import BaseModel

# Always validate external API responses
sureify_data = await sureify.get_contact()
validated = ClientModel(**sureify_data)  # Pydantic validates
```

### 2. Don't Store Secrets in Database

```python
# ❌ Bad: Storing Sureify credentials in DB
# ✅ Good: Environment variables
SUREIFY_CLIENT_ID = os.getenv("SUREIFY_CLIENT_ID")
```

### 3. Rate Limit User Requests

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.get("/alerts")
@limiter.limit("100/minute")  # Max 100 requests per minute
async def get_alerts():
    ...
```

---

## Testing Strategy

### 1. Test Each Pattern Separately

```python
# Test local DB pattern
def test_get_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200

# Test fetch & merge pattern (mock Sureify)
def test_get_client_profile(mock_sureify):
    mock_sureify.get_contact.return_value = {"name": "John"}
    response = client.get("/api/clients/123/profile")
    assert "name" in response.json()
```

### 2. Integration Tests

```python
# Test full flow with real database
async def test_client_override_flow():
    # 1. Get default profile
    profile = await get_client_profile("123")

    # 2. Save override
    await update_client_profile_overrides("123", {"notes": "Test"})

    # 3. Verify override applied
    updated = await get_client_profile("123")
    assert updated["notes"] == "Test"
```

---

## Summary: Your Architecture

```
┌────────────────────────────────────────┐
│   ONE FastAPI App                      │
│   ────────────────                     │
│                                        │
│   Routers by Domain:                   │
│   • alerts.py    → PostgreSQL          │
│   • clients.py   → Sureify + PG        │
│   • products.py  → Sureify (cached)    │
│   • passthrough  → Direct Sureify      │
│                                        │
│   Benefits:                            │
│   ✅ Simple deployment                 │
│   ✅ Shared resources                  │
│   ✅ Easy debugging                    │
│   ✅ Fast development                  │
└────────────────────────────────────────┘
```

**Pattern Guide:**
- **Alerts** = Local DB (you own the data)
- **Profiles** = Fetch & Merge (real-time + overrides)
- **Products** = Cache (rarely changes)
- **Passthrough** = Direct proxy (admin/debug)

This gives you the **best balance** of:
- Performance (caching where needed)
- Freshness (real-time where important)
- Simplicity (one deployment)
- Flexibility (different patterns per endpoint)

Perfect for a hackathon! 🚀
