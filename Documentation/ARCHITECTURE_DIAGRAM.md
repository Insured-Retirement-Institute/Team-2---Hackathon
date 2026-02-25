# Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph "Frontend"
        UI[React UI<br/>S3 Static Site<br/>hackathon-team2-ui.s3...amazonaws.com]
    end

    subgraph "Backend - FastAPI Application (Port 8000)"
        API[FastAPI App<br/>api.main:app]

        subgraph "Routers"
            ALERTS[Alerts Router<br/>/api/alerts<br/>/api/dashboard/stats]
            CLIENTS[Clients Router<br/>/api/clients/{id}/profile]
            PRODUCTS[Products Router<br/>/passthrough/products]
            PASSTHROUGH[Passthrough Router<br/>/passthrough/*]
            POLICIES[Policies Router<br/>/v2/policies]
        end

        API --> ALERTS
        API --> CLIENTS
        API --> PRODUCTS
        API --> PASSTHROUGH
        API --> POLICIES
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>RDS)]
        SUREIFY[Sureify API<br/>hackathon-dev-api.sureify.com]
        COGNITO[AWS Cognito<br/>OAuth2 Token]
    end

    subgraph "Database Tables"
        T1[renewal_alerts]
        T2[client_profile_overrides]
        T3[contract_summary]
        T4[products]
    end

    %% User interactions
    UI -->|HTTP GET/POST| API

    %% Alerts flow
    ALERTS -->|Read/Write| T1
    ALERTS -->|Stats queries| DB

    %% Clients flow (Fetch & Merge)
    CLIENTS -->|1. Fetch base data| SUREIFY
    CLIENTS -->|2. Fetch overrides| T2
    CLIENTS -->|3. Merge & return| UI

    %% Products flow (Proxy)
    PRODUCTS -->|Proxy request| SUREIFY
    PASSTHROUGH -->|Direct proxy| SUREIFY

    %% Policies flow
    POLICIES -->|Query| T3

    %% Database connections
    DB --> T1
    DB --> T2
    DB --> T3
    DB --> T4

    %% Authentication
    PASSTHROUGH -->|1. Get token| COGNITO
    CLIENTS -->|1. Get token| COGNITO
    PRODUCTS -->|1. Get token| COGNITO
    COGNITO -->|2. Access token| SUREIFY

    %% Styling
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef backend fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef data fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef router fill:#fff9c4,stroke:#f57f17,stroke-width:1px

    class UI frontend
    class API,ALERTS,CLIENTS,PRODUCTS,PASSTHROUGH,POLICIES backend
    class DB,SUREIFY,COGNITO,T1,T2,T3,T4 data
    class ALERTS,CLIENTS,PRODUCTS,PASSTHROUGH,POLICIES router
```

## Data Flow Patterns

```mermaid
sequenceDiagram
    participant UI as React UI
    participant API as FastAPI
    participant DB as PostgreSQL
    participant SUREIFY as Sureify API
    participant COGNITO as AWS Cognito

    Note over UI,COGNITO: Pattern 1: Local Database Only (Alerts)
    UI->>API: GET /api/alerts
    API->>DB: SELECT FROM renewal_alerts
    DB-->>API: Alert rows
    API-->>UI: JSON response

    Note over UI,COGNITO: Pattern 2: Fetch & Merge (Client Profiles)
    UI->>API: GET /api/clients/123/profile
    API->>COGNITO: POST /oauth2/token
    COGNITO-->>API: Access token
    API->>SUREIFY: GET /puddle/contacts (with token)
    SUREIFY-->>API: Base profile data
    API->>DB: SELECT FROM client_profile_overrides
    DB-->>API: Local overrides
    Note over API: Merge base + overrides
    API-->>UI: Combined profile

    Note over UI,COGNITO: Pattern 3: Direct Proxy (Passthrough)
    UI->>API: GET /passthrough/products
    API->>COGNITO: POST /oauth2/token
    COGNITO-->>API: Access token
    API->>SUREIFY: GET /puddle/products (with token)
    SUREIFY-->>API: Product data
    API-->>UI: Proxy response
```

## Component Diagram

```mermaid
graph LR
    subgraph "FastAPI Application"
        M[main.py<br/>App Entry Point]

        subgraph "Routers"
            R1[alerts.py]
            R2[clients.py]
            R3[passthrough.py]
            R4[policies.py]
        end

        subgraph "Shared Components"
            DB[database.py<br/>Connection Pool]
            SC[sureify_client.py<br/>OAuth2 Client]
            MOD[sureify_models.py<br/>Pydantic Models]
        end

        M --> R1
        M --> R2
        M --> R3
        M --> R4

        R1 --> DB
        R2 --> DB
        R2 --> SC
        R3 --> SC
        R4 --> DB

        SC --> MOD
    end

    subgraph "SQL Queries"
        Q1[get_alerts.sql]
        Q2[get_dashboard_stats.sql]
        Q3[snooze_alert.sql]
    end

    DB --> Q1
    DB --> Q2
    DB --> Q3
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "Frontend"
            S3[S3 Bucket<br/>Static Website<br/>React Build]
            CF[CloudFront<br/>CDN]
        end

        subgraph "Backend"
            ALB[Application<br/>Load Balancer]
            ECS[ECS Fargate<br/>Container Service]
            ECR[ECR<br/>Docker Registry]
        end

        subgraph "Data"
            RDS[RDS PostgreSQL<br/>team2-postgresql-db]
        end

        subgraph "External"
            SUREIFY_API[Sureify API<br/>hackathon-dev-api]
            COGNITO[Cognito<br/>OAuth2]
        end
    end

    USER[User Browser] --> CF
    CF --> S3
    CF --> ALB
    ALB --> ECS
    ECS --> RDS
    ECS --> SUREIFY_API
    ECS --> COGNITO

    DEV[Developer] -->|docker push| ECR
    ECR -->|deploy| ECS
```

## Technology Stack

```mermaid
mindmap
    root((IRI Hackathon<br/>Tech Stack))
        Frontend
            React
            TypeScript
            Swagger UI
        Backend
            Python 3.13
            FastAPI
            Uvicorn
            Pydantic
        Database
            PostgreSQL
            asyncpg
            SQL queries
        External APIs
            Sureify CoreCONNECT
            AWS Cognito OAuth2
        Infrastructure
            Docker
            AWS ECS
            AWS RDS
            AWS S3
            CloudFront
        Development
            uv package manager
            pytest
            curl/httpx
```

## View in GitHub

These diagrams use **Mermaid** syntax and will render automatically in:
- ✅ GitHub README.md
- ✅ VS Code (with Mermaid extension)
- ✅ GitLab
- ✅ Many markdown viewers

## Generate PNG/SVG

To convert to image files:

```bash
# Install mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i ARCHITECTURE_DIAGRAM.md -o architecture.png

# Generate SVG
mmdc -i ARCHITECTURE_DIAGRAM.md -o architecture.svg
```

Or use online tools:
- https://mermaid.live/
- Copy/paste the diagram code
- Export as PNG/SVG/PDF
