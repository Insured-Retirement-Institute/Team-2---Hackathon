#!/usr/bin/env python3
"""
Test script for the IRI Alerts API endpoints.
Run this after starting the FastAPI server to verify everything works.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_get_alerts():
    """Test GET /api/alerts"""
    print_section("TEST: GET /api/alerts")

    response = requests.get(f"{BASE_URL}/alerts")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        alerts = response.json()
        print(f"Found {len(alerts)} alerts")
        if alerts:
            print("\nFirst alert:")
            print(json.dumps(alerts[0], indent=2))
    else:
        print(f"Error: {response.text}")


def test_get_alerts_filtered():
    """Test GET /api/alerts with filters"""
    print_section("TEST: GET /api/alerts?priority=high")

    response = requests.get(f"{BASE_URL}/alerts", params={"priority": "high"})
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        alerts = response.json()
        print(f"Found {len(alerts)} high-priority alerts")
    else:
        print(f"Error: {response.text}")


def test_get_dashboard_stats():
    """Test GET /api/dashboard/stats"""
    print_section("TEST: GET /api/dashboard/stats")

    response = requests.get(f"{BASE_URL}/dashboard/stats")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        stats = response.json()
        print("\nDashboard Statistics:")
        print(json.dumps(stats, indent=2))
    else:
        print(f"Error: {response.text}")


def test_get_alert_detail():
    """Test GET /api/alerts/{alertId}"""
    print_section("TEST: GET /api/alerts/{alertId}")

    alert_id = "alert-ANN-2020-5621-renewal"
    response = requests.get(f"{BASE_URL}/alerts/{alert_id}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        alert = response.json()
        print(f"\nAlert Detail for {alert_id}:")
        print(json.dumps(alert, indent=2))
    else:
        print(f"Error: {response.text}")


def test_snooze_alert():
    """Test POST /api/alerts/{alertId}/snooze"""
    print_section("TEST: POST /api/alerts/{alertId}/snooze")

    alert_id = "alert-ANN-2019-3412-renewal"
    payload = {
        "snoozeDays": 7,
        "reason": "Testing snooze functionality"
    }

    response = requests.post(
        f"{BASE_URL}/alerts/{alert_id}/snooze",
        json=payload
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\nSnooze Result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")


def test_dismiss_alert():
    """Test POST /api/alerts/{alertId}/dismiss"""
    print_section("TEST: POST /api/alerts/{alertId}/dismiss")

    alert_id = "alert-ANN-2021-7823-data"
    payload = {
        "reason": "Testing dismiss functionality"
    }

    response = requests.post(
        f"{BASE_URL}/alerts/{alert_id}/dismiss",
        json=payload
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\nDismiss Result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.text}")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  IRI ALERTS API TEST SUITE")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")

    try:
        # Test all endpoints
        test_get_alerts()
        test_get_alerts_filtered()
        test_get_dashboard_stats()
        test_get_alert_detail()
        test_snooze_alert()
        test_dismiss_alert()

        print("\n" + "=" * 70)
        print("  ALL TESTS COMPLETED")
        print("=" * 70)

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to the API server.")
        print(f"Make sure the FastAPI server is running at {BASE_URL}")
        print("\nStart it with:")
        print("  cd api")
        print("  uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
