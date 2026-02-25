#!/usr/bin/env python3
"""
Test all UI-required endpoints to ensure they work before connecting the UI.
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_endpoint(method, path, description, **kwargs):
    """Test a single endpoint"""
    print(f"\nTesting: {description}")
    print(f"  {method} {path}")

    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{path}", **kwargs)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{path}", **kwargs)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{path}", **kwargs)
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{path}", **kwargs)

        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("  [OK]")
            return True
        elif response.status_code == 404:
            print("  [WARN] Not found (may need sample data)")
            return False
        else:
            print(f"  [ERROR] {response.text[:100]}")
            return False

    except requests.exceptions.ConnectionError:
        print("  [ERROR] Cannot connect to API")
        print("\n" + "=" * 70)
        print("  Make sure API server is running:")
        print("  cd api && uvicorn api.main:app --reload")
        print("=" * 70)
        exit(1)
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    print("=" * 70)
    print("  UI ENDPOINT VERIFICATION TEST")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")

    results = {}

    # Test CORS preflight
    print("\n" + "-" * 70)
    print("  CORS Configuration")
    print("-" * 70)
    response = requests.options(f"{BASE_URL}/api/alerts")
    cors_ok = "access-control-allow-origin" in response.headers
    print(f"CORS Headers: {'[OK]' if cors_ok else '[WARN] Missing'}")
    results["CORS"] = cors_ok

    # Test Dashboard & Alerts
    print("\n" + "-" * 70)
    print("  Dashboard & Alerts Endpoints")
    print("-" * 70)

    results["GET /api/alerts"] = test_endpoint(
        "GET", "/api/alerts",
        "Get all alerts"
    )

    results["GET /api/dashboard/stats"] = test_endpoint(
        "GET", "/api/dashboard/stats",
        "Get dashboard statistics"
    )

    results["GET /api/alerts/{id}"] = test_endpoint(
        "GET", "/api/alerts/alert-ANN-2020-5621-renewal",
        "Get specific alert"
    )

    # Test Client Profiles
    print("\n" + "-" * 70)
    print("  Client Profile Endpoints")
    print("-" * 70)

    results["GET /api/clients/{id}/profile"] = test_endpoint(
        "GET", "/api/clients/1003/profile",
        "Get client profile (override-first)"
    )

    # Test Products
    print("\n" + "-" * 70)
    print("  Product Endpoints")
    print("-" * 70)

    results["GET /api/products/shelf"] = test_endpoint(
        "GET", "/api/products/shelf",
        "Get product shelf"
    )

    # Test Passthrough
    print("\n" + "-" * 70)
    print("  Passthrough Endpoints")
    print("-" * 70)

    results["GET /passthrough/products"] = test_endpoint(
        "GET", "/passthrough/products?user_id=1003&persona=agent",
        "Passthrough to Sureify products"
    )

    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for endpoint, status in results.items():
        status_str = "[OK]" if status else "[FAIL]"
        print(f"  {status_str} {endpoint}")

    print("-" * 70)
    print(f"  Passed: {passed}/{total}")
    print("=" * 70)

    if passed == total:
        print("\n[OK] All endpoints working! UI can connect.")
    else:
        print("\n[WARN] Some endpoints failed. Check:")
        print("  1. Is the API server running?")
        print("  2. Has sample data been loaded?")
        print("     python scripts/populate_alerts.py")
        print("  3. Are Sureify credentials configured?")

    print("\nNext steps:")
    print("  1. Start UI: npm start (in UI project)")
    print("  2. Configure UI API URL: http://localhost:8000")
    print("  3. Open UI in browser")


if __name__ == "__main__":
    main()
