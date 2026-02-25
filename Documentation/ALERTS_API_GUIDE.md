# IRI Alerts API Implementation Guide

## Architecture Overview

The IRI Dashboard follows a **pull-based architecture** where the UI fetches data from the backend API:

```
┌──────────────────────┐
│   React UI           │  ← User opens in browser
│   (S3 Static Site)   │
└──────────┬───────────┘
           │ HTTP GET/POST
           │ (UI pulls data)
           ↓
┌──────────────────────┐
│   FastAPI Backend    │  ← Implements IRI API spec
│   /api/alerts        │
│   /api/dashboard/    │
│      stats           │
└──────────┬───────────┘
           │
           ├──→ PostgreSQL Database
           │    (renewal_alerts table)
           │
           └──→ Sureify API
                (external insurance data)
```

## Database Schema

The `renewal_alerts` table stores alert data with the following structure:

- **id**: Unique alert identifier (e.g., "alert-ANN-2020-5621-renewal")
- **policy_id**: Reference to contract_summary.contract_id
- **client_name**: Policy owner name
- **carrier**: Insurance carrier
- **renewal_date**: Human-readable renewal date (e.g., "15 Days")
- **days_until_renewal**: Numeric days until renewal
- **current_rate**: Current interest rate
- **renewal_rate**: New renewal rate
- **current_value**: Current policy value
- **priority**: "high", "medium", or "low"
- **status**: "pending", "reviewed", "snoozed", or "dismissed"
- **alert_type**: Type of alert (replacement_recommended, etc.)
- **alert_detail**: JSONB field for full alert detail data
- **snoozed_until**: Timestamp for snoozed alerts

## API Endpoints Implemented

### 1. GET /api/alerts
**Purpose**: List all renewal alerts (dashboard view)
**Query Parameters**:
- `status` (optional): Filter by status
- `priority` (optional): Filter by priority
- `carrier` (optional): Filter by carrier

**Response**: Array of RenewalAlert objects

### 2. GET /api/dashboard/stats
**Purpose**: Get dashboard statistics summary
**Response**: DashboardStats object with:
- `total`: Total number of alerts
- `high`: Number of high priority alerts
- `urgent`: Number of alerts with ≤30 days until renewal
- `totalValue`: Sum of all alert policy values

### 3. GET /api/alerts/{alertId}
**Purpose**: Get detailed information for a specific alert
**Response**: Full AlertDetail object (if stored in alert_detail JSONB) or RenewalAlert object

### 4. POST /api/alerts/{alertId}/snooze
**Purpose**: Snooze an alert for a specified number of days
**Request Body**:
```json
{
  "snoozeDays": 30,
  "reason": "Waiting for client response"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Alert snoozed for 30 days",
  "snoozeUntil": "2026-03-26T20:00:00"
}
```

### 5. POST /api/alerts/{alertId}/dismiss
**Purpose**: Dismiss an alert permanently
**Request Body**:
```json
{
  "reason": "Not applicable"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Alert dismissed successfully"
}
```

## Setup Instructions

### 1. Create the Database Table
```bash
# Apply the database schema
psql $DATABASE_URL -f database/tables/renewal_alerts.sql
```

### 2. Populate Sample Data
```bash
# Load sample alerts for testing
python scripts/populate_alerts.py
```

### 3. Start the FastAPI Server
```bash
cd api
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the Endpoints
```bash
# Get all alerts
curl http://localhost:8000/api/alerts

# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats

# Get specific alert
curl http://localhost:8000/api/alerts/alert-ANN-2020-5621-renewal

# Snooze an alert
curl -X POST http://localhost:8000/api/alerts/alert-ANN-2020-5621-renewal/snooze \
  -H "Content-Type: application/json" \
  -d '{"snoozeDays": 30, "reason": "Test"}'

# Filter by priority
curl "http://localhost:8000/api/alerts?priority=high"
```

## How the UI Interacts with the API

### On Dashboard Load
1. UI makes `GET /api/alerts` to fetch all alerts
2. UI makes `GET /api/dashboard/stats` to fetch statistics
3. Displays the data in the dashboard interface

### When User Clicks an Alert
1. UI makes `GET /api/alerts/{alertId}` to fetch detailed information
2. Displays full alert details, policy information, and actions

### When User Snoozes/Dismisses
1. UI makes `POST /api/alerts/{alertId}/snooze` or `POST /api/alerts/{alertId}/dismiss`
2. Backend updates the database
3. UI refreshes the alert list

## Data Flow: Populating Alerts

You have several options for populating alerts:

### Option 1: From Sureify API + Business Logic
```python
# Example: Generate alerts from Sureify policies
# (This would go in api/scripts/generate_alerts.py)
from api.sureify_client import SureifyClient
from agents.logic import check_replacement_opportunity

# Fetch policies from Sureify
policies = await client.get_policies(user_id="1003", persona=Persona.agent)

# Apply business logic to identify alerts
for policy in policies:
    if check_replacement_opportunity(policy):
        # Insert alert into renewal_alerts table
        await create_alert(policy)
```

### Option 2: From Agent Analysis
```python
# Use the existing agents package
from agents.main import get_book_of_business_as_iri_alerts

# The agent analyzes Sureify data and generates alerts
alerts_data = await get_book_of_business_as_iri_alerts()

# Insert into database
for alert in alerts_data["alerts"]:
    await insert_alert(alert)
```

### Option 3: Manual/Scheduled Job
```python
# Create a scheduled job (cron/celery) that:
# 1. Fetches latest policy data from Sureify
# 2. Applies business rules
# 3. Updates the renewal_alerts table
```

## Best Practices

1. **Use JSONB for Flexibility**: The `alert_detail` column stores complex nested data as JSON
2. **Index Common Queries**: Indexes exist on status, priority, carrier, and policy_id
3. **Handle Snoozed Alerts**: The query automatically filters out snoozed alerts whose snooze period hasn't expired
4. **Use Pydantic Models**: Import from `agents/iri_schemas.py` for type safety
5. **Error Handling**: All endpoints return appropriate HTTP status codes (404, 400, etc.)

## Environment Variables

Make sure these are set:
```bash
DATABASE_URL=postgresql://app_user:password@host:5432/postgres
SUREIFY_CLIENT_ID=your_client_id
SUREIFY_CLIENT_SECRET=your_client_secret
```

## Next Steps

1. **Implement Additional Endpoints**: Compare tab, product shelf, etc.
2. **Add Authentication**: Protect endpoints with JWT/OAuth
3. **Create Alert Generation Logic**: Automate alert creation from Sureify data
4. **Add Audit Logging**: Track all alert actions
5. **Configure CORS**: Allow requests from your UI domain

## Testing with the UI

Once your backend is running:

1. Configure the UI to point to your API:
   - Development: `http://localhost:8000/api`
   - Production: Your deployed backend URL

2. The UI will automatically:
   - Fetch alerts on page load
   - Display them in the dashboard
   - Allow filtering, snoozing, and dismissing
   - Show detailed views when clicked

The API spec at `/api-spec-v3.yaml` defines the complete contract between UI and backend.
