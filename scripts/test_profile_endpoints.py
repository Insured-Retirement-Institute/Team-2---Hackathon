#!/usr/bin/env python3
"""
Test client profile and suitability endpoints.
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
            try:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                pass
            return True
        elif response.status_code == 404:
            print("  [WARN] Not found (expected if no data exists yet)")
            return False
        else:
            print(f"  [ERROR] {response.text[:200]}")
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
    print("  PROFILE & SUITABILITY ENDPOINT TEST")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")

    results = {}

    # Test Client Profile Endpoints
    print("\n" + "-" * 70)
    print("  Client Profile Endpoints")
    print("-" * 70)

    # Test GET profile (will fetch from Sureify if not in DB)
    results["GET /api/clients/{clientId}/profile"] = test_endpoint(
        "GET", "/api/clients/1003/profile",
        "Get client profile (DB-first, fallback to Sureify)"
    )

    # Test PUT profile
    profile_data = {
        "grossIncome": "85000",
        "disposableIncome": "45000",
        "taxBracket": "22%",
        "householdLiquidAssets": "250000",
        "monthlyLivingExpenses": "4500",
        "financialObjectives": "Supplement Social Security with guaranteed income",
        "distributionPlan": "Systematic withdrawals beginning at age 67",
        "residesInNursingHome": "no",
        "hasLongTermCareInsurance": "yes"
    }

    results["PUT /api/clients/{clientId}/profile"] = test_endpoint(
        "PUT", "/api/clients/1003/profile",
        "Save client profile parameters",
        json=profile_data,
        headers={"Content-Type": "application/json"}
    )

    # Test GET profile again (should now return from DB)
    results["GET /api/clients/{clientId}/profile (from DB)"] = test_endpoint(
        "GET", "/api/clients/1003/profile",
        "Get client profile (should return from DB this time)"
    )

    # Test Suitability Endpoint
    print("\n" + "-" * 70)
    print("  Suitability Endpoints")
    print("-" * 70)

    # Note: This test requires an alert with customer_identifier set
    suitability_data = {
        "clientObjectives": "Preserve principal with modest growth; generate guaranteed retirement income",
        "riskTolerance": "Conservative",
        "timeHorizon": "5-10 years",
        "liquidityNeeds": "Low -- has separate emergency fund covering 12 months",
        "taxConsiderations": "Currently in 22% bracket; expects 12% bracket in retirement",
        "guaranteedIncome": "Desires guaranteed income floor of $2,000/month",
        "rateExpectations": "Willing to accept lower current rate for longer guarantee",
        "surrenderTimeline": "No anticipated need to surrender within next 7 years",
        "livingBenefits": ["Nursing home waiver", "Terminal illness benefit"],
        "advisorEligibility": "Series 6, state insurance license -- all appointments current",
        "score": 82,
        "isPrefilled": False
    }

    results["PUT /alerts/{alertId}/suitability"] = test_endpoint(
        "PUT", "/api/alerts/test-alert-001/suitability",
        "Save suitability data for alert",
        json=suitability_data,
        headers={"Content-Type": "application/json"}
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
        print("\n[OK] All endpoints working!")
    else:
        print("\n[WARN] Some endpoints failed. Check:")
        print("  1. Is the API server running?")
        print("  2. Has the database been initialized with new tables?")
        print("     psql -f database/main.sql")
        print("  3. Do alerts have customer_identifier set?")

    print("\nNotes:")
    print("  - GET profile will fetch from Sureify if no DB record exists")
    print("  - PUT suitability requires alert with customer_identifier")
    print("  - Profile must be fetched at least once before suitability can be saved")


if __name__ == "__main__":
    main()
