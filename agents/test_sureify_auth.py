"""
Test Sureify auth (Option A: SUREIFY_BASE_URL + SUREIFY_BEARER_TOKEN).
Loads .env from repo root, then calls the shared client and one Puddle endpoint.

Run from repo root:
  PYTHONPATH=. python -m agents.test_sureify_auth
Or with explicit .env:
  PYTHONPATH=. python -m agents.test_sureify_auth  # uses .env in cwd
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Repo root = parent of agents/
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Load .env from repo root (Option A: SUREIFY_BEARER_TOKEN)
_env = _repo_root / ".env"
if _env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env)
    except ImportError:
        pass


def main() -> None:
    base = os.environ.get("SUREIFY_BASE_URL", "").strip()
    token = os.environ.get("SUREIFY_BEARER_TOKEN", "").strip()

    if not base:
        print("FAIL: SUREIFY_BASE_URL is not set. Set it in .env or export it.")
        sys.exit(1)
    if not token:
        print("FAIL: SUREIFY_BEARER_TOKEN is not set (Option A). Add your token to .env or export SUREIFY_BEARER_TOKEN.")
        sys.exit(1)
    # Mask token in output
    token_preview = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***"

    print("Using Option A: SUREIFY_BASE_URL + SUREIFY_BEARER_TOKEN")
    print(f"  SUREIFY_BASE_URL={base}")
    print(f"  SUREIFY_BEARER_TOKEN={token_preview}")

    from agents.sureify_client import _get_authenticated_client, get_products

    client = _get_authenticated_client()
    if client is None:
        print("FAIL: _get_authenticated_client() returned None (auth failed or no token).")
        sys.exit(1)
    print("  Authenticated client obtained.")

    # Call one Puddle endpoint (productOption) to verify token works
    try:
        options = get_products("1001")
    except Exception as e:
        err = str(e)
        print(f"FAIL: API call failed: {e}")
        if "401" in err:
            print("  Hint: Token may be expired or invalid. Refresh SUREIFY_BEARER_TOKEN and try again.")
        sys.exit(1)

    count = len(options) if isinstance(options, list) else 0
    print(f"  GET /puddle/productOption: OK ({count} product(s) returned).")
    print("SUCCESS: Sureify Option A auth and Puddle API call work.")


if __name__ == "__main__":
    main()
