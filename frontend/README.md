# IRI Dashboard - Frontend

Annuity Renewal Intelligence Dashboard for the IRI Hackathon.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **shadcn/ui** (Radix UI) for components
- **Node.js 22** (via nvm)

## Getting Started

### Prerequisites

- Node.js 22 (use nvm: `nvm use 22`)
- npm 10+

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

The app will be available at `http://localhost:5173`

## Project Structure

```
frontend/
├── docs/
│   └── api-spec.yaml          # OpenAPI specification for backend team
├── src/
│   ├── api/
│   │   ├── mock/
│   │   │   └── alerts.ts      # 🔴 MOCK DATA - Replace with real API
│   │   └── alerts.ts          # API service layer
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── AlertsTable.tsx    # Alerts table component
│   │   └── StatsCards.tsx     # Dashboard stat cards
│   ├── pages/
│   │   └── Dashboard.tsx      # Main dashboard page
│   ├── types/
│   │   └── alerts.ts          # TypeScript type definitions
│   ├── lib/
│   │   └── utils.ts           # Utility functions
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Mock Data Location

**⚠️ IMPORTANT:** All mock data is located in `src/api/mock/`

The API service layer (`src/api/alerts.ts`) currently returns mock data. To integrate with real APIs:

1. Update the API functions in `src/api/alerts.ts`
2. Remove the mock data imports
3. Uncomment the real fetch calls
4. Update `API_BASE_URL` in environment variables

## API Specification

The OpenAPI specification for the backend team is located at:
```
docs/api-spec.yaml
```

This spec defines:
- `GET /api/alerts` - Fetch all renewal alerts
- `GET /api/alerts/{alertId}` - Fetch specific alert
- `POST /api/alerts/{alertId}/snooze` - Snooze an alert
- `POST /api/alerts/{alertId}/dismiss` - Dismiss an alert
- `GET /api/dashboard/stats` - Fetch dashboard statistics

## Dashboard Features

### Current Implementation (v1)

- ✅ 4 stat cards (Total Alerts, High Priority, Urgent, Total Value)
- ✅ Renewal alerts table with:
  - Client name
  - Policy ID
  - Carrier
  - Current value
  - Renewal date
  - Rate change visualization
  - Priority badges
  - Status indicators
  - Data exception warnings

### Coming Soon

- Alert detail modal
- Snooze/dismiss functionality
- Filters and search
- Grouped alerts view
- Discussion activity widget

## Environment Variables

Create a `.env` file in the root:

```env
VITE_API_BASE_URL=http://localhost:3000/api
```

## Development Notes

- Using Tailwind CSS v4 with `@tailwindcss/vite` plugin
- Path aliases configured: `@/` maps to `src/`
- TypeScript strict mode enabled
- Mock data simulates 300ms API delay for realistic UX

## Backend Integration

Share `docs/api-spec.yaml` with the backend team. The spec includes:
- Complete request/response schemas
- Example payloads
- Error handling patterns
- Query parameters for filtering

The frontend is ready to consume these APIs once implemented.
