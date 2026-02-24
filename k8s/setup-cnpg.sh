#!/bin/bash
set -euo pipefail

# CloudNativePG Setup Script
# Ensures kubectl context is set to local cluster (orbstack/kind)

CNPG_VERSION="${CNPG_VERSION:-1.28.1}"

echo "=== Installing CloudNativePG v${CNPG_VERSION} ==="

# Install CNPG operator
kubectl apply --server-side -f \
  "https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.28/releases/cnpg-${CNPG_VERSION}.yaml"

echo "=== Waiting for CNPG operator to be ready ==="
kubectl wait --for=condition=Available deployment/cnpg-controller-manager \
  -n cnpg-system --timeout=300s

echo "=== Creating pgschema password secret ==="
kubectl create secret generic pgschema-password \
  --from-literal=username=pgschema \
  --from-literal=password="$(openssl rand -base64 24)" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "=== Deploying PostgreSQL cluster ==="
kubectl apply -f "$(dirname "$0")/dev-cluster.yaml"

echo "=== Waiting for PostgreSQL cluster to be ready ==="
kubectl wait --for=condition=Ready cluster/sds-dev --timeout=600s

echo "=== CNPG setup complete ==="
echo ""
echo "Connection info:"
kubectl get secret sds-dev-superuser -o jsonpath='{.data}' | jq -r 'to_entries[] | "\(.key): \(.value | @base64d)"'
