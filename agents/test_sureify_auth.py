"""
Test API server passthrough connectivity.

Verifies that the API server is reachable and the passthrough endpoints return
data from Sureify. The API server handles Sureify auth (OAuth / bearer token).

Run from repo root:
  PYTHONPATH=. python -m agents.test_sureify_auth
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
_env = _repo_root / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass

import httpx


def main() -> None:
    base = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
    print(f"API_BASE_URL={base}")

    # Health check
    try:
        r = httpx.get(f"{base}/health", timeout=10)
        r.raise_for_status()
        health = r.json()
        print(f"  /health: {health}")
    except Exception as e:
        print(f"FAIL: API server not reachable at {base}/health: {e}")
        sys.exit(1)

    # Passthrough product-options
    try:
        r = httpx.get(f"{base}/passthrough/product-options", timeout=30)
        r.raise_for_status()
        products = r.json()
        count = len(products) if isinstance(products, list) else 0
        print(f"  /passthrough/product-options: OK ({count} product(s) returned)")
    except Exception as e:
        print(f"FAIL: /passthrough/product-options call failed: {e}")
        sys.exit(1)

    # Passthrough policy-data
    try:
        r = httpx.get(f"{base}/passthrough/policy-data", timeout=30)
        r.raise_for_status()
        policies = r.json()
        count = len(policies) if isinstance(policies, list) else 0
        print(f"  /passthrough/policy-data: OK ({count} polic(ies) returned)")
    except Exception as e:
        print(f"FAIL: /passthrough/policy-data call failed: {e}")
        sys.exit(1)

    print("SUCCESS: API server passthrough endpoints are working.")


if __name__ == "__main__":
    main()
