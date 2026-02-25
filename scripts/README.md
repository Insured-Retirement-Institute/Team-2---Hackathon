# Scripts Directory

Utility scripts for setup, testing, and data exploration.

## Setup Scripts

### populate_alerts.py
Populates the `renewal_alerts` table with sample data for testing.

```bash
cd /c/Hackathon/code
python scripts/populate_alerts.py
```

**Purpose:** Load demo data into the database so the API has alerts to return.

---

## Data Exploration Scripts

### list_products.py
Fetches and displays all product names from the Sureify API.

```bash
python scripts/list_products.py
```

**Output:** List of all 13 products with names and codes.

### get_products.py
Alternative product fetching script using the Python async client.

```bash
export SUREIFY_CLIENT_ID="..."
export SUREIFY_CLIENT_SECRET="..."
python scripts/get_products.py
```

**Purpose:** Example of using the SureifyClient programmatically.

---

## Diagram Generation Scripts

### generate_simple_diagram.py
Generates architecture diagrams as PNG files.

```bash
# Install dependencies
pip install diagrams
# Also requires Graphviz: choco install graphviz (Windows)

# Generate diagrams
python scripts/generate_simple_diagram.py
# Output: diagrams/*.png
```

**See [DIAGRAM_GUIDE.md](../DIAGRAM_GUIDE.md) for full instructions.**

---

## Testing Scripts

### test_alerts_api.py
Integration tests for the IRI Alerts API endpoints.

```bash
# Start the API first
cd api
uvicorn api.main:app --reload

# Then run tests
python scripts/test_alerts_api.py
```

**Tests:**
- GET /api/alerts
- GET /api/alerts?priority=high
- GET /api/dashboard/stats
- GET /api/alerts/{alertId}
- POST /api/alerts/{alertId}/snooze
- POST /api/alerts/{alertId}/dismiss

---

## Quick Start

```bash
# 1. Create database tables
psql $DATABASE_URL -f database/tables/renewal_alerts.sql

# 2. Load sample data
python scripts/populate_alerts.py

# 3. Start API server
cd api && uvicorn api.main:app --reload

# 4. Test endpoints
python scripts/test_alerts_api.py
```

---

## Script Organization

- **Setup scripts** - Run once to initialize data
- **Data exploration** - Query external APIs to understand data
- **Testing scripts** - Verify API endpoints work correctly

All scripts are standalone and can be run from the project root.
