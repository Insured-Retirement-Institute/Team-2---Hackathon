# API Implementation Status

Status of IRI Dashboard API endpoints for the UI at:
`http://hackathon-team2-ui.s3-website-us-east-1.amazonaws.com`

## ✅ Fully Implemented (Core Functionality)

### Dashboard & Alerts
| Endpoint | Method | Status | Router | Description |
|----------|--------|--------|--------|-------------|
| `/api/alerts` | GET | ✅ | alerts.py | List all renewal alerts with filters |
| `/api/dashboard/stats` | GET | ✅ | alerts.py | Dashboard statistics |
| `/api/alerts/{alertId}` | GET | ✅ | alerts.py | Get alert details |
| `/api/alerts/{alertId}/snooze` | POST | ✅ | alerts.py | Snooze an alert |
| `/api/alerts/{alertId}/dismiss` | POST | ✅ | alerts.py | Dismiss an alert |

### Client Profiles
| Endpoint | Method | Status | Router | Description |
|----------|--------|--------|--------|-------------|
| `/api/clients/{clientId}/profile` | GET | ✅ | clients.py | Get client profile (override-first) |
| `/api/clients/{clientId}/profile` | PUT | ✅ | clients.py | Save profile overrides |
| `/api/clients/{clientId}/profile/overrides` | DELETE | ✅ | clients.py | Clear overrides |

### Products
| Endpoint | Method | Status | Router | Description |
|----------|--------|--------|--------|-------------|
| `/api/products/shelf` | GET | ✅ | products.py | Product catalog for comparison |

### Passthrough (Sureify Direct Access)
| Endpoint | Method | Status | Router | Description |
|----------|--------|--------|--------|-------------|
| `/passthrough/applications` | GET | ✅ | passthrough.py | Direct Sureify access |
| `/passthrough/cases` | GET | ✅ | passthrough.py | Direct Sureify access |
| `/passthrough/policies` | GET | ✅ | passthrough.py | Direct Sureify access |
| `/passthrough/products` | GET | ✅ | passthrough.py | Direct Sureify access |
| `/passthrough/contacts` | GET | ✅ | passthrough.py | Direct Sureify access |
| ...and 10 more | GET | ✅ | passthrough.py | All Sureify endpoints |

---

## 🚧 Optional (Not Critical for Basic Demo)

These endpoints are in the UI spec but not required for basic functionality:

| Endpoint | Method | Status | Notes |
|----------|--------|--------|-------|
| `/api/alerts/{alertId}/compare` | POST | ⏸️ | Product comparison analysis |
| `/api/alerts/{alertId}/compare/products` | POST | ⏸️ | Re-compare with selected products |
| `/api/alerts/{alertId}/suitability` | GET/POST | ⏸️ | Suitability assessment |
| `/api/alerts/{alertId}/disclosures` | POST | ⏸️ | Compliance disclosures |
| `/api/alerts/{alertId}/transaction` | POST | ⏸️ | Transaction submission |

**Why optional:**
- Core dashboard functionality works without them
- UI can gracefully handle 404 responses
- Can be implemented iteratively as needed

---

## 🔧 Configuration Status

### CORS (Cross-Origin Resource Sharing)
✅ **Configured** - UI can call API

Allowed origins:
- `http://hackathon-team2-ui.s3-website-us-east-1.amazonaws.com`
- `http://localhost:3000` (local dev)
- `http://localhost:5173` (Vite dev server)

### Database Tables
✅ **Created**
- `renewal_alerts` - Alert data
- `client_profile_overrides` - Client profile overrides

### Authentication
✅ **Working**
- Sureify OAuth2 via AWS Cognito
- Automatic token refresh

---

## 📊 Implementation Details

### `/api/clients/{clientId}/profile` Logic

**Updated per requirements:**

```
1. Check override table
   ├─ If exists → Return override data ✅
   └─ If not → Fetch from Sureify passthrough ✅
```

**Previous behavior:** Always fetched from Sureify and merged overrides
**New behavior:** Override-first, only fetch from Sureify if no override exists

### `/api/products/shelf` Logic

```
1. Fetch from Sureify (with auth)
2. Cache for 15 minutes (optional enhancement)
3. Filter by carrier, type (query params)
4. Return product list
```

---

## 🚀 Quick Start

### 1. Start the API Server

```bash
cd api
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Point UI to Your API

Update UI environment config to:
```
API_BASE_URL=http://localhost:8000
```

### 3. Load Sample Data

```bash
python scripts/populate_alerts.py
```

### 4. Test Endpoints

```bash
# Get alerts
curl http://localhost:8000/api/alerts

# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats

# Get client profile (checks override first)
curl http://localhost:8000/api/clients/1003/profile

# Get products shelf
curl http://localhost:8000/api/products/shelf
```

---

## 🔍 Testing the Override Logic

### Test: Client Profile Override-First

```bash
# 1. Get profile (will fetch from Sureify since no override)
curl http://localhost:8000/api/clients/1003/profile

# 2. Save an override
curl -X PUT http://localhost:8000/api/clients/1003/profile \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "1003",
    "risk_tolerance": "aggressive",
    "investment_objectives": "Growth",
    "notes": "Prefers tech stocks"
  }'

# 3. Get profile again (will return override, skip Sureify)
curl http://localhost:8000/api/clients/1003/profile
# Returns: override data only

# 4. Clear override
curl -X DELETE http://localhost:8000/api/clients/1003/profile/overrides

# 5. Get profile again (will fetch from Sureify again)
curl http://localhost:8000/api/clients/1003/profile
```

---

## 📝 API Response Examples

### GET /api/alerts

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
    "alertDescription": "Renewal rate drops from 3.8% to 1.5%..."
  }
]
```

### GET /api/clients/1003/profile (with override)

```json
{
  "client_id": "1003",
  "risk_tolerance": "aggressive",
  "investment_objectives": "Growth",
  "notes": "Prefers tech stocks",
  "created_at": "2026-02-25T10:00:00",
  "updated_at": "2026-02-25T10:00:00"
}
```

### GET /api/products/shelf

```json
[
  {
    "ID": "F645wXH9XXm-qUOyh1GyYQ",
    "productCode": "a007",
    "name": "Variable Annuity (VA)",
    "carrierCode": "carrier-123"
  },
  {
    "ID": "jwX5OIxcXjaJJyMvVJGiuw",
    "productCode": "a003",
    "name": "Market Watch (Index Annuity)",
    "carrierCode": "carrier-456"
  }
]
```

---

## 🐛 Troubleshooting

### CORS Error in Browser

**Symptom:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** Make sure UI origin is in allowed origins list (already configured)

### 404 on /api/alerts

**Symptom:** `{"detail": "Not Found"}`

**Solution:**
1. Check server is running
2. Ensure alerts router is registered in main.py ✅
3. Populate sample data: `python scripts/populate_alerts.py`

### Empty alerts list

**Symptom:** Returns `[]`

**Solution:** Run `python scripts/populate_alerts.py` to load sample data

### Client profile returns 404

**Symptom:** `{"detail": "Client 1003 not found in Sureify"}`

**Solution:**
- Ensure Sureify credentials are configured
- Check client ID exists in Sureify
- Or create a profile override first

---

## 📚 Related Documentation

- [ALERTS_API_GUIDE.md](ALERTS_API_GUIDE.md) - Alerts API implementation details
- [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - Data patterns and architecture
- [DIAGRAM_GUIDE.md](DIAGRAM_GUIDE.md) - Visual architecture diagrams
- [API Spec (UI)](http://hackathon-team2-ui.s3-website-us-east-1.amazonaws.com/api-spec) - Full UI API specification

---

## ✅ Summary

**Ready for UI Integration:**
- ✅ Core endpoints implemented
- ✅ CORS configured
- ✅ Client profile override-first logic
- ✅ Product shelf endpoint
- ✅ Database tables created
- ✅ Sample data available

**What's Working:**
1. Dashboard displays alerts ✅
2. Alert details view ✅
3. Snooze/dismiss alerts ✅
4. Client profiles (override-first) ✅
5. Product shelf ✅

**Next Steps (Optional):**
- Implement comparison endpoints
- Add caching layer for products
- Implement suitability/disclosures
- Add pagination for large datasets
