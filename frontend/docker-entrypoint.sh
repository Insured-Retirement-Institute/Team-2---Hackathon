#!/bin/sh
set -e

# Generate runtime config from environment variables
cat > /usr/share/nginx/html/config.js << EOF
window.__APP_CONFIG__ = {
  useMocks: ${USE_MOCKS:-false},
  apiBaseUrl: "${API_BASE_URL:-/api}"
};
EOF

# Start nginx
exec nginx -g 'daemon off;'
