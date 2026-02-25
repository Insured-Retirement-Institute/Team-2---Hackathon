#!/usr/bin/env python3
"""
Script to populate the renewal_alerts table with sample data for testing.
Run this after creating the renewal_alerts table.
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app_user@localhost:5432/postgres")


async def populate_alerts():
    """Populate sample alert data"""
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Sample alert data based on the IRI API spec
        sample_alerts = [
            {
                "id": "alert-ANN-2020-5621-renewal",
                "policy_id": "ANN-2020-5621",
                "client_name": "Maria Rodriguez",
                "carrier": "Athene",
                "renewal_date": "15 Days",
                "days_until_renewal": 15,
                "current_rate": "3.8%",
                "renewal_rate": "1.5%",
                "current_value": "$180,000",
                "is_min_rate": True,
                "priority": "high",
                "has_data_exception": False,
                "status": "pending",
                "alert_type": "replacement_recommended",
                "alert_description": "Renewal rate drops from 3.8% to 1.5% (minimum guarantee). Consider replacement with higher-yielding product.",
            },
            {
                "id": "alert-ANN-2019-3412-renewal",
                "policy_id": "ANN-2019-3412",
                "client_name": "John Smith",
                "carrier": "Pacific Life",
                "renewal_date": "30 Days",
                "days_until_renewal": 30,
                "current_rate": "4.2%",
                "renewal_rate": "2.1%",
                "current_value": "$250,000",
                "is_min_rate": False,
                "priority": "medium",
                "has_data_exception": False,
                "status": "pending",
                "alert_type": "replacement_opportunity",
                "alert_description": "Rate renewal approaching. Current rate 4.2%, renewal rate 2.1%. Explore alternatives.",
            },
            {
                "id": "alert-ANN-2021-7823-data",
                "policy_id": "ANN-2021-7823",
                "client_name": "Sarah Johnson",
                "carrier": "Nationwide",
                "renewal_date": "45 Days",
                "days_until_renewal": 45,
                "current_rate": "3.5%",
                "renewal_rate": "3.0%",
                "current_value": "$150,000",
                "is_min_rate": False,
                "priority": "low",
                "has_data_exception": True,
                "missing_fields": ["beneficiary", "suitability_profile"],
                "status": "pending",
                "alert_type": "missing_info",
                "alert_description": "Missing beneficiary and suitability profile information. Complete data before renewal.",
            },
            {
                "id": "alert-ANN-2018-9001-suit",
                "policy_id": "ANN-2018-9001",
                "client_name": "Michael Chen",
                "carrier": "Allianz",
                "renewal_date": "60 Days",
                "days_until_renewal": 60,
                "current_rate": "4.0%",
                "renewal_rate": "3.5%",
                "current_value": "$320,000",
                "is_min_rate": False,
                "priority": "high",
                "has_data_exception": False,
                "status": "pending",
                "alert_type": "suitability_review",
                "alert_description": "High-value policy requires updated suitability review before renewal decision.",
            },
            {
                "id": "alert-ANN-2020-4512-income",
                "policy_id": "ANN-2020-4512",
                "client_name": "Linda Williams",
                "carrier": "American Equity",
                "renewal_date": "90 Days",
                "days_until_renewal": 90,
                "current_rate": "3.2%",
                "renewal_rate": "2.8%",
                "current_value": "$195,000",
                "is_min_rate": False,
                "priority": "medium",
                "has_data_exception": False,
                "status": "pending",
                "alert_type": "income_planning",
                "alert_description": "Client approaching retirement age. Consider income planning options and riders.",
            },
        ]

        # Insert alerts
        for alert in sample_alerts:
            await conn.execute(
                """
                INSERT INTO renewal_alerts (
                    id, policy_id, client_name, carrier, renewal_date,
                    days_until_renewal, current_rate, renewal_rate, current_value,
                    is_min_rate, priority, has_data_exception, missing_fields,
                    status, alert_type, alert_description
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
                )
                ON CONFLICT (id) DO UPDATE SET
                    client_name = EXCLUDED.client_name,
                    carrier = EXCLUDED.carrier,
                    renewal_date = EXCLUDED.renewal_date,
                    days_until_renewal = EXCLUDED.days_until_renewal,
                    current_rate = EXCLUDED.current_rate,
                    renewal_rate = EXCLUDED.renewal_rate,
                    current_value = EXCLUDED.current_value,
                    is_min_rate = EXCLUDED.is_min_rate,
                    priority = EXCLUDED.priority,
                    has_data_exception = EXCLUDED.has_data_exception,
                    missing_fields = EXCLUDED.missing_fields,
                    status = EXCLUDED.status,
                    alert_type = EXCLUDED.alert_type,
                    alert_description = EXCLUDED.alert_description,
                    updated_at = now()
                """,
                alert["id"],
                alert["policy_id"],
                alert["client_name"],
                alert["carrier"],
                alert["renewal_date"],
                alert["days_until_renewal"],
                alert["current_rate"],
                alert["renewal_rate"],
                alert["current_value"],
                alert["is_min_rate"],
                alert["priority"],
                alert["has_data_exception"],
                alert.get("missing_fields"),
                alert["status"],
                alert["alert_type"],
                alert["alert_description"],
            )

        print(f"✓ Successfully inserted/updated {len(sample_alerts)} alerts")

        # Display summary
        count = await conn.fetchval("SELECT COUNT(*) FROM renewal_alerts")
        print(f"\nTotal alerts in database: {count}")

        # Show breakdown by status
        status_counts = await conn.fetch(
            """
            SELECT status, COUNT(*) as count
            FROM renewal_alerts
            GROUP BY status
            ORDER BY status
            """
        )
        print("\nAlerts by status:")
        for row in status_counts:
            print(f"  {row['status']}: {row['count']}")

    finally:
        await conn.close()


if __name__ == "__main__":
    print("Populating renewal_alerts table with sample data...")
    asyncio.run(populate_alerts())
