#!/usr/bin/env python3
"""
Generate architecture diagrams for the IRI Hackathon project.
Creates PNG files showing system architecture, data flow, and component relationships.

Installation:
    pip install diagrams graphviz

Note: Requires Graphviz to be installed on your system:
    - Windows: choco install graphviz
    - Mac: brew install graphviz
    - Linux: apt-get install graphviz

Usage:
    python scripts/generate_architecture_diagram.py
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import ECS
from diagrams.aws.database import RDS
from diagrams.aws.network import ALB, CloudFront
from diagrams.aws.storage import S3
from diagrams.aws.security import Cognito
from diagrams.onprem.client import Users
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.custom import Custom
import os

# Create output directory
os.makedirs("diagrams", exist_ok=True)

# Graph attributes for better styling
graph_attr = {
    "fontsize": "12",
    "bgcolor": "white",
    "pad": "0.5",
}

node_attr = {
    "fontsize": "11",
}

edge_attr = {
    "fontsize": "10",
}


def create_system_architecture():
    """Create high-level system architecture diagram"""
    with Diagram(
        "IRI Hackathon - System Architecture",
        filename="diagrams/system_architecture",
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        users = Users("Advisors\n(Browser)")

        with Cluster("AWS Cloud"):
            with Cluster("Frontend"):
                ui = S3("React UI\n(S3 Static Site)")
                cdn = CloudFront("CloudFront CDN")

            with Cluster("Backend (FastAPI)"):
                alb = ALB("Load Balancer")
                api = ECS("FastAPI Container\n(ECS Fargate)")

            with Cluster("Data Layer"):
                db = RDS("PostgreSQL\n(RDS)")

            with Cluster("External APIs"):
                cognito = Cognito("AWS Cognito\n(OAuth2)")

        # External service (outside AWS)
        sureify = Custom("Sureify API\n(External)", "./sureify_icon.png")

        # User flow
        users >> Edge(label="HTTPS") >> cdn
        cdn >> Edge(label="Static\nAssets") >> ui
        cdn >> Edge(label="API\nRequests") >> alb
        alb >> Edge(label="Load\nBalance") >> api

        # Backend connections
        api >> Edge(label="Query\nAlerts") >> db
        api >> Edge(label="Auth\nToken") >> cognito
        api >> Edge(label="Fetch\nPolicies", style="dashed") >> sureify
        cognito >> Edge(label="Validate", style="dotted") >> sureify


def create_data_flow_diagram():
    """Create detailed data flow diagram"""
    with Diagram(
        "IRI Hackathon - Data Flow Patterns",
        filename="diagrams/data_flow",
        show=False,
        direction="LR",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        users = Users("React UI")

        with Cluster("FastAPI Application"):
            with Cluster("Pattern 1: Local DB Only"):
                alerts_router = Python("Alerts Router\n/api/alerts")
                alerts_db = RDS("renewal_alerts\ntable")
                alerts_router >> Edge(label="SELECT") >> alerts_db

            with Cluster("Pattern 2: Fetch & Merge"):
                clients_router = Python("Clients Router\n/api/clients")
                overrides_db = RDS("client_profile\n_overrides")
                cognito = Cognito("OAuth2")
                sureify = Custom("Sureify API", "./sureify_icon.png")

                clients_router >> Edge(label="1. Auth") >> cognito
                clients_router >> Edge(label="2. Fetch") >> sureify
                clients_router >> Edge(label="3. Get\nOverrides") >> overrides_db

            with Cluster("Pattern 3: Direct Proxy"):
                passthrough = Python("Passthrough\nRouter")
                passthrough >> Edge(label="Proxy") >> sureify

        # User interactions
        users >> Edge(label="GET /api/alerts") >> alerts_router
        users >> Edge(label="GET /api/clients/{id}") >> clients_router
        users >> Edge(label="GET /passthrough/*") >> passthrough


def create_component_diagram():
    """Create component/module diagram"""
    with Diagram(
        "IRI Hackathon - Component Structure",
        filename="diagrams/component_structure",
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        with Cluster("FastAPI Application"):
            main = FastAPI("main.py\n(App Entry)")

            with Cluster("Routers"):
                alerts = Python("alerts.py\n/api/alerts")
                clients = Python("clients.py\n/api/clients")
                products = Python("products.py\n/passthrough/products")
                policies = Python("policies.py\n/v2/policies")

            with Cluster("Shared Components"):
                db = Python("database.py\n(Connection Pool)")
                sureify_client = Python("sureify_client.py\n(OAuth2 Client)")
                models = Python("sureify_models.py\n(Pydantic)")

            with Cluster("SQL Queries"):
                sql1 = Python("get_alerts.sql")
                sql2 = Python("get_dashboard_stats.sql")
                sql3 = Python("snooze_alert.sql")

        # Router registration
        main >> Edge(label="include") >> alerts
        main >> Edge(label="include") >> clients
        main >> Edge(label="include") >> products
        main >> Edge(label="include") >> policies

        # Shared component usage
        alerts >> Edge(label="uses") >> db
        clients >> Edge(label="uses") >> db
        clients >> Edge(label="uses") >> sureify_client
        products >> Edge(label="uses") >> sureify_client
        policies >> Edge(label="uses") >> db

        sureify_client >> Edge(label="uses") >> models

        # SQL query loading
        db >> Edge(label="loads", style="dashed") >> sql1
        db >> Edge(label="loads", style="dashed") >> sql2
        db >> Edge(label="loads", style="dashed") >> sql3


def create_deployment_diagram():
    """Create deployment architecture diagram"""
    with Diagram(
        "IRI Hackathon - Deployment Architecture",
        filename="diagrams/deployment",
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
    ):
        with Cluster("Development"):
            dev = Users("Developer")

        with Cluster("AWS Cloud - us-east-1"):
            with Cluster("Frontend Hosting"):
                s3 = S3("S3 Bucket\nhackathon-team2-ui")
                cf = CloudFront("CloudFront\nDistribution")

            with Cluster("Backend (ECS)"):
                ecr = Custom("ECR\nDocker Registry", "./docker_icon.png")
                ecs = ECS("ECS Fargate\n1+ Containers")
                alb_backend = ALB("Application\nLoad Balancer")

            with Cluster("Data Layer"):
                rds = RDS("RDS PostgreSQL\nteam2-postgresql-db")

        with Cluster("External Services"):
            sureify = Custom("Sureify API\nhackathon-dev-api", "./sureify_icon.png")
            cognito = Cognito("AWS Cognito\nOAuth2")

        # Deployment flow
        dev >> Edge(label="docker build\n& push") >> ecr
        ecr >> Edge(label="deploy") >> ecs

        # Runtime connections
        cf >> s3
        cf >> alb_backend >> ecs
        ecs >> Edge(label="queries") >> rds
        ecs >> Edge(label="auth") >> cognito
        ecs >> Edge(label="API calls") >> sureify


def main():
    """Generate all diagrams"""
    print("Generating architecture diagrams...")

    try:
        print("1. Creating system architecture diagram...")
        create_system_architecture()
        print("   ✓ diagrams/system_architecture.png")

        print("2. Creating data flow diagram...")
        create_data_flow_diagram()
        print("   ✓ diagrams/data_flow.png")

        print("3. Creating component structure diagram...")
        create_component_diagram()
        print("   ✓ diagrams/component_structure.png")

        print("4. Creating deployment diagram...")
        create_deployment_diagram()
        print("   ✓ diagrams/deployment.png")

        print("\n" + "=" * 60)
        print("✓ All diagrams generated successfully!")
        print("=" * 60)
        print("\nGenerated files:")
        print("  - diagrams/system_architecture.png")
        print("  - diagrams/data_flow.png")
        print("  - diagrams/component_structure.png")
        print("  - diagrams/deployment.png")
        print("\nOpen these files to view your architecture diagrams.")

    except Exception as e:
        print(f"\n❌ Error generating diagrams: {e}")
        print("\nMake sure you have installed:")
        print("  1. pip install diagrams")
        print("  2. Graphviz (system-level):")
        print("     - Windows: choco install graphviz")
        print("     - Mac: brew install graphviz")
        print("     - Linux: apt-get install graphviz")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
