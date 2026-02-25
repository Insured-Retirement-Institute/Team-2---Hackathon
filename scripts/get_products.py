#!/usr/bin/env python3
"""
Script to authenticate with Sureify API and retrieve all product names.
"""
import asyncio
import sys
import os

# Add the api/src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api', 'src'))

from api.sureify_client import SureifyClient, SureifyAuthConfig
from api.sureify_models import Persona


async def main():
    """Main function to get products from Sureify API."""

    # Initialize the client with credentials from environment variables
    print("Initializing Sureify client...")
    config = SureifyAuthConfig()

    # Check if credentials are configured
    if not config.client_id or not config.client_secret:
        print("\n[ERROR] Sureify credentials not configured!")
        print("\nPlease set the following environment variables:")
        print("  - SUREIFY_CLIENT_ID")
        print("  - SUREIFY_CLIENT_SECRET")
        print("  - SUREIFY_BASE_URL (optional, defaults to hackathon-dev-api.sureify.com)")
        print("  - SUREIFY_TOKEN_URL (optional, defaults to Cognito endpoint)")
        print("  - SUREIFY_SCOPE (optional, defaults to hackathon-dev-EdgeApiM2M/edge)")
        print("\nOr create a mise.local.toml file with the credentials as shown in api/README.md")
        return

    async with SureifyClient(config) as client:
        # Authenticate and get token
        print("Authenticating with Sureify API...")
        token = await client.authenticate()
        print(f"[SUCCESS] Authenticated! Token: {token[:20]}...")

        # Get products - requires persona parameter
        print("\nFetching products from /puddle/products endpoint...")
        products = await client.get_products(user_id="1003", persona=Persona.agent)
        print(f"[SUCCESS] Retrieved {len(products)} products")

        # Extract product names
        print("\n" + "="*60)
        print("PRODUCT NAMES:")
        print("="*60)

        product_names = []
        for i, product in enumerate(products, 1):
            name = product.name if product.name else "(No name)"
            product_code = product.productCode if product.productCode else "(No code)"
            product_names.append(name)
            print(f"{i:3d}. {name} (Code: {product_code})")

        print("="*60)
        print(f"\nTotal products: {len(product_names)}")

        # Return the list
        return product_names


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
