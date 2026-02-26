"""
Test API passthrough connectivity. Verifies API_BASE_URL and a passthrough endpoint.

Run from repo root:
  PYTHONPATH=. python -m agents.test_sureify_auth
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

_env = _repo_root / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass

_API_BASE = os.environ.get("API_BASE_URL", "http://k8s-default-hack2fut-959780892e-989138425.us-east-1.elb.amazonaws.com/api").rstrip("/")


def main() -> None:
    if not _API_BASE:
        print("FAIL: API_BASE_URL is not set. Set it in .env or export it (e.g. http://.../api).")
        sys.exit(1)

    print(f"API_BASE_URL={_API_BASE}")
    print("  Calling GET /passthrough/product-options ...")

    try:
        with httpx.Client(timeout=60.0) as client:
            r = client.get(f"{_API_BASE}/passthrough/product-options", params={"user_id": "1001", "persona": "agent"})
            r.raise_for_status()
            options = r.json()
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)

    count = len(options) if isinstance(options, list) else 0
    print(f"  OK ({count} product option(s) returned).")
    print("SUCCESS: Passthrough API is reachable.")


if __name__ == "__main__":
    main()
