#!/usr/bin/env python3
"""
Simple architecture diagram generator (no custom icons required).
Generates PNG files showing your application architecture.

Installation:
    pip install diagrams graphviz

System requirement:
    Graphviz must be installed:
    - Windows: choco install graphviz (or download from graphviz.org)
    - Mac: brew install graphviz
    - Linux: apt-get install graphviz

Usage:
    python scripts/generate_simple_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import ECS
from diagrams.aws.database import RDS, ElasticacheCacheNode
from diagrams.aws.network import ALB, CloudFront, Route53
from diagrams.aws.storage import S3
from diagrams.aws.security import Cognito
from diagrams.onprem.client import Users, Client
from diagrams.programming.framework import Fastapi
from diagrams.programming.language import Python
from diagrams.generic.storage import Storage
from diagrams.generic.database import SQL
import os

# Create output directory
os.makedirs("diagrams", exist_ok=True)


def create_main_architecture():
    """Create the main system architecture diagram"""

    with Diagram(
        "IRI Hackathon - Main Architecture",
        filename="diagrams/main_architecture",
        show=False,
        direction="TB",
        outformat="png",
    ):
        users = Users("Financial Advisors")

        with Cluster("React UI (S3)"):
            ui = S3("Static Website\nhackathon-team2-ui")

        with Cluster("FastAPI Backend"):
            api = Fastapi("FastAPI App\nPort 8000")

            with Cluster("Routers"):
                alerts = Python("Alerts\n/api/alerts")
                clients = Python("Clients\n/api/clients")
                products = Python("Products\n/passthrough/products")

        with Cluster("Data Sources"):
            postgres = RDS("PostgreSQL\nRDS")
            sureify = Storage("Sureify API\n(External)")
            auth = Cognito("OAuth2\nCognito")

        # Connections
        users >> Edge(label="HTTPS") >> ui
        ui >> Edge(label="API calls") >> api

        api >> alerts >> Edge(label="Read/Write") >> postgres
        api >> clients >> Edge(label="Fetch") >> sureify
        clients >> Edge(label="Merge") >> postgres
        api >> products >> Edge(label="Proxy") >> sureify

        products >> Edge(label="Auth") >> auth
        clients >> Edge(label="Auth") >> auth
        auth >> Edge(label="Token") >> sureify


def create_data_patterns():
    """Create diagram showing data access patterns"""

    with Diagram(
        "Data Access Patterns",
        filename="diagrams/data_patterns",
        show=False,
        direction="LR",
        outformat="png",
    ):
        ui = Client("UI")

        with Cluster("Pattern 1: Local DB"):
            p1_api = Python("GET /api/alerts")
            p1_db = SQL("renewal_alerts")
            ui >> p1_api >> p1_db

        with Cluster("Pattern 2: Fetch & Merge"):
            p2_api = Python("GET /api/clients/{id}")
            p2_ext = Storage("Sureify\nBase Data")
            p2_db = SQL("Overrides")
            ui >> p2_api
            p2_api >> Edge(label="1") >> p2_ext
            p2_api >> Edge(label="2") >> p2_db
            p2_api >> Edge(label="3. Merge") >> ui

        with Cluster("Pattern 3: Cached"):
            p3_api = Python("GET /products")
            p3_cache = ElasticacheCacheNode("Cache\n15 min")
            p3_ext = Storage("Sureify")
            ui >> p3_api
            p3_api >> p3_cache
            p3_cache >> Edge(label="Miss") >> p3_ext


def create_database_schema():
    """Create database schema diagram"""

    with Diagram(
        "Database Schema",
        filename="diagrams/database_schema",
        show=False,
        direction="TB",
        outformat="png",
    ):
        with Cluster("PostgreSQL Tables"):
            with Cluster("Your Data"):
                alerts = SQL("renewal_alerts\n- id\n- policy_id\n- priority\n- status")
                overrides = SQL("client_profile_overrides\n- client_id\n- risk_tolerance\n- notes")

            with Cluster("Sureify Mirror"):
                contracts = SQL("contract_summary\n- contract_id\n- product_name\n- carrier")
                products_tbl = SQL("products\n- product_id\n- name\n- type")

        alerts >> Edge(label="FK") >> contracts
        overrides >> Edge(label="Reference") >> contracts


def create_deployment():
    """Create deployment diagram"""

    with Diagram(
        "Deployment Architecture",
        filename="diagrams/deployment_arch",
        show=False,
        direction="TB",
        outformat="png",
    ):
        dev = Users("Developer")

        with Cluster("AWS us-east-1"):
            with Cluster("Frontend"):
                s3 = S3("S3 Bucket")
                cdn = CloudFront("CloudFront")

            with Cluster("Backend"):
                alb = ALB("ALB")
                ecs = ECS("ECS Fargate\nDocker Container")

            with Cluster("Database"):
                rds = RDS("RDS PostgreSQL")

        with Cluster("External"):
            sureify = Storage("Sureify API")

        # Flow
        dev >> Edge(label="Deploy") >> s3
        dev >> Edge(label="Deploy") >> ecs

        cdn >> s3
        cdn >> alb >> ecs
        ecs >> rds
        ecs >> sureify


def main():
    """Generate all diagrams"""
    print("\n" + "=" * 70)
    print("  IRI HACKATHON - ARCHITECTURE DIAGRAM GENERATOR")
    print("=" * 70)

    try:
        import diagrams
        print("\n[OK] Diagrams library installed")
    except ImportError:
        print("\n[ERROR] Error: 'diagrams' library not installed")
        print("\nInstall with:")
        print("  pip install diagrams")
        return

    print("\nGenerating diagrams...")
    print("-" * 70)

    try:
        print("1. Main Architecture...")
        create_main_architecture()
        print("   [OK] diagrams/main_architecture.png")

        print("2. Data Access Patterns...")
        create_data_patterns()
        print("   [OK] diagrams/data_patterns.png")

        print("3. Database Schema...")
        create_database_schema()
        print("   [OK] diagrams/database_schema.png")

        print("4. Deployment Architecture...")
        create_deployment()
        print("   [OK] diagrams/deployment_arch.png")

        print("\n" + "=" * 70)
        print("  [OK] SUCCESS! All diagrams generated")
        print("=" * 70)
        print("\nGenerated files in 'diagrams/' folder:")
        print("  - main_architecture.png")
        print("  - data_patterns.png")
        print("  - database_schema.png")
        print("  - deployment_arch.png")
        print("\nTIP: Tip: Open these PNG files to view your architecture!")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nTroubleshooting:")
        print("1. Install Graphviz (system-level):")
        print("   Windows: choco install graphviz")
        print("   Mac: brew install graphviz")
        print("   Linux: apt-get install graphviz")
        print("\n2. Restart your terminal after installing Graphviz")
        print("\n3. Verify installation:")
        print("   dot -V")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
