#!/usr/bin/env bash
# Connect to Team 2 RDS PostgreSQL. Run from repo root.
# 1. Add your DB password to .env as RDS_PASSWORD=
# 2. Run: ./connect-db.sh   (or: source .env && ./connect-db.sh)

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CERT="${SCRIPT_DIR}/certs/global-bundle.pem"

if [[ -f "${SCRIPT_DIR}/.env" ]]; then
  set -a
  source "${SCRIPT_DIR}/.env"
  set +a
fi

if [[ -z "${RDSHOST}" ]]; then
  echo "Error: RDSHOST not set. Add it to .env or export RDSHOST=..."
  exit 1
fi

if [[ -z "${RDS_PASSWORD}" ]]; then
  echo "RDS_PASSWORD not set in .env; psql will prompt for password."
  export PGPASSWORD=""
else
  export PGPASSWORD="${RDS_PASSWORD}"
fi

psql "host=${RDSHOST} port=5432 dbname=postgres user=${RDS_USER:-app_user} sslmode=verify-full sslrootcert=${CERT}"
