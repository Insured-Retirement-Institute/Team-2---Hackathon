#!/usr/bin/env python3
"""Simple script to list product names from Sureify API using curl"""
import subprocess
import json

# Generate token
print("Generating token...")
token_cmd = [
    'curl', '--request', 'POST',
    'https://hackathon-dev-sureify.auth.us-west-2.amazoncognito.com/oauth2/token',
    '--header', 'Content-Type: application/x-www-form-urlencoded',
    '--data-urlencode', 'grant_type=client_credentials',
    '--data-urlencode', 'client_id=4feqlovadmoi5qsk0i2lob0f98',
    '--data-urlencode', 'client_secret=h5r2v7un0vg84g9ao0irq3dp4olpp1futvlfk0juu6ov0njaepc',
    '--data-urlencode', 'scope=hackathon-dev-EdgeApiM2M/edge',
    '-s'
]

token_result = subprocess.run(token_cmd, capture_output=True, text=True)
token_data = json.loads(token_result.stdout)
access_token = token_data['access_token']
print(f"Token generated: {access_token[:20]}...\n")

# Fetch products
print("Fetching products...")
products_cmd = [
    'curl', '-s',
    'https://hackathon-dev-api.sureify.com/puddle/products?persona=agent',
    '-H', f'Authorization: Bearer {access_token}',
    '-H', 'UserID: 1003'
]

products_result = subprocess.run(products_cmd, capture_output=True, text=True)
products = json.loads(products_result.stdout)

# Extract products array from the response
products_list = products.get('products', [])

# Display products
print("=" * 70)
print("ALL PRODUCT NAMES FROM SUREIFY API")
print("=" * 70)
print()

for i, product in enumerate(products_list, 1):
    name = product.get('name', '(No name)')
    code = product.get('productCode', 'N/A')
    print(f"{i:2d}. {name:45s} (Code: {code})")

print()
print("=" * 70)
print(f"Total: {len(products_list)} products")
print("=" * 70)

# Extract just the names as a list
product_names = [p.get('name', '(No name)') for p in products_list]
print("\nProduct names only:")
for name in product_names:
    print(f"  - {name}")
