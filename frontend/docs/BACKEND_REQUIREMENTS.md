# Backend API Requirements - IRI Dashboard

## Overview

This document outlines the API requirements for the IRI Annuity Renewal Intelligence Dashboard. The frontend is built and ready to integrate with these endpoints.

## Quick Start

1. Review the OpenAPI specification: `docs/api-spec.yaml`
2. Implement the endpoints listed below
3. Return mock data initially (same structure as frontend mock data in `src/api/mock/alerts.ts`)
4. Frontend will consume APIs via `src/api/alerts.ts`

## Required Endpoints

### 1. Get All Alerts
```
GET /api/alerts
```

**Query Parameters:**
- `status` (optional): `pending` | `reviewed` | `snoozed` | `dismissed`
- `priority` (optional): `high` | `medium` | `low`
- `carrier` (optional): carrier name string

**Response:** Array of `RenewalAlert` objects

**Example Response:**
```json
[
  {
    "id": "alert-ANN-2020-5621-renewal",
    "policyId": "ANN-2020-5621",
    "clientName": "Maria Rodriguez",
    "carrier": "Athene",
    "renewalDate": "15 Days",
    "daysUntilRenewal": 15,
    "currentRate": "3.8%",
    "renewalRate": "1.5%",
    "currentValue": "$180,000",
    "isMinRate": true,
    "priority": "high",
    "hasDataException": false,
    "status": "pending",
    "alertType": "replacement_recommended",
    "alertTypes": ["replacement_recommended", "suitability_review", "missing_info"],
    "alertDescription": "Renewal at minimum rate - replacement analysis recommended"
  },
  {
    "id": "alert-ANN-2020-7845-missing",
    "policyId": "ANN-2020-7845",
    "clientName": "Daniel Garcia",
    "carrier": "Pacific Life",
    "renewalDate": "N/A",
    "daysUntilRenewal": 74,
    "currentRate": "3.9%",
    "renewalRate": "2.9%",
    "currentValue": "$178,000",
    "isMinRate": false,
    "priority": "low",
    "hasDataException": true,
    "missingFields": ["Contact phone update needed"],
    "status": "pending",
    "alertType": "missing_info",
    "alertDescription": "Client contact information needs update"
  }
]
```

### 2. Get Dashboard Statistics
```
GET /api/dashboard/stats
```

**Response:**
```json
{
  "total": 10,
  "high": 3,
  "urgent": 4,
  "totalValue": 1839000
}
```

**Calculation Logic:**
- `total`: Count of all active alerts
- `high`: Count of alerts with `priority = "high"`
- `urgent`: Count of alerts with `daysUntilRenewal <= 30`
- `totalValue`: Sum of all `currentValue` amounts (numeric, not formatted)

### 3. Snooze Alert
```
POST /api/alerts/{alertId}/snooze
```

**Request Body:**
```json
{
  "snoozeDays": 7,
  "reason": "Waiting for client response"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Alert snoozed successfully",
  "snoozeUntil": "2026-03-03T00:00:00Z"
}
```

### 4. Dismiss Alert
```
POST /api/alerts/{alertId}/dismiss
```

**Request Body:**
```json
{
  "reason": "Client declined replacement"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Alert dismissed successfully"
}
```

## Data Models

### RenewalAlert
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique alert ID (e.g., `"alert-ANN-2020-5621-renewal"`) |
| `policyId` | string | yes | Policy identifier (e.g., `"ANN-2020-5621"`) |
| `clientName` | string | yes | Client full name |
| `carrier` | string | yes | Insurance carrier (Athene, Nationwide, Allianz, Pacific Life) |
| `renewalDate` | string | yes | Human-readable (e.g., `"15 Days"` or `"N/A"`) |
| `daysUntilRenewal` | integer | yes | Numeric days count |
| `currentRate` | string | yes | Formatted rate (e.g., `"3.8%"`) |
| `renewalRate` | string | yes | Formatted rate (e.g., `"1.5%"`) |
| `currentValue` | string | yes | Formatted currency (e.g., `"$180,000"`) |
| `isMinRate` | boolean | yes | True if renewal at minimum guaranteed rate |
| `priority` | string | yes | `"high"` \| `"medium"` \| `"low"` |
| `hasDataException` | boolean | yes | Data quality flag |
| `missingFields` | string[] | no | Present when `hasDataException` is true |
| `status` | string | yes | `"pending"` \| `"reviewed"` \| `"snoozed"` \| `"dismissed"` |
| `alertType` | string | yes | See Alert Types below |
| `alertTypes` | string[] | no | All applicable alert types for this client/policy |
| `alertDescription` | string | yes | Human-readable description |

### Alert Types
| Value | Description |
|-------|-------------|
| `replacement_recommended` | Renewal at minimum rate, replacement analysis recommended |
| `replacement_opportunity` | Replacement opportunity identified |
| `suitability_review` | Annual suitability review required |
| `missing_info` | Client data needs update |
| `income_planning` | Client approaching income distribution phase |

### DashboardStats
| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total active alerts |
| `high` | integer | High priority count |
| `urgent` | integer | Alerts within 30 days |
| `totalValue` | number | Sum of policy values in dollars (numeric) |

## Notes

- **CORS**: Enable for local development (frontend runs on port 5173)
- **Currency values**: Return as formatted strings with `$` and commas
- **Rates**: Return as formatted strings with `%`
- **Dates**: Use human-readable format for `renewalDate` (e.g., `"15 Days"`, `"N/A"`)
- **Multiple alerts per client**: A single client can have multiple alerts (e.g., Maria Rodriguez has both a replacement and suitability alert). The frontend groups these by `clientName`.

## Frontend Integration

The frontend calls these APIs from `src/api/alerts.ts`:
- `fetchAlerts()` → `GET /api/alerts`
- `fetchDashboardStats()` → `GET /api/dashboard/stats`
- `snoozeAlert(alertId, days)` → `POST /api/alerts/{alertId}/snooze`
- `dismissAlert(alertId, reason)` → `POST /api/alerts/{alertId}/dismiss`

Set `VITE_API_BASE_URL` in `.env` to point to the backend.
