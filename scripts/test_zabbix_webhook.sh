#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_DIR}/.env"

if [ -f "${ENV_FILE}" ]; then
    WEBHOOK_API_KEY=$(grep -E '^WEBHOOK_API_KEY=' "${ENV_FILE}" | cut -d'=' -f2- | tr -d '"')
else
    echo "Warning: .env not found at ${ENV_FILE}, using default WEBHOOK_API_KEY"
fi
WEBHOOK_API_KEY="${WEBHOOK_API_KEY:-changeme-webhook-api-key}"
BASE_URL="${BASE_URL:-http://localhost:8000}"
PAYLOAD_FILE="${PROJECT_DIR}/mock/zabbix_real_payload_example.json"

mask_api_key() {
    local key="$1"
    local len=${#key}
    if [ "${len}" -gt 8 ]; then
        echo "${key:0:4}****${key: -4}"
    else
        echo "****"
    fi
}

API_KEY_DISPLAY=$(mask_api_key "${WEBHOOK_API_KEY}")

WEBHOOK_URL="${BASE_URL}/api/v1/webhooks/zabbix"
HEALTH_URL="${BASE_URL}/api/v1/health"
ALERTS_URL="${BASE_URL}/api/v1/alerts"

echo "=== AIOps Zabbix Monitor - Real Webhook Test ==="
echo ""
echo "Project dir : ${PROJECT_DIR}"
echo "Backend URL : ${BASE_URL}"
echo "Payload     : ${PAYLOAD_FILE}"
echo "API Key     : ${API_KEY_DISPLAY}"
echo ""

echo "=== Step 1: Health Check ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${HEALTH_URL}")
if [ "${HTTP_CODE}" = "200" ]; then
    echo "Backend is healthy (HTTP ${HTTP_CODE})"
else
    echo "Backend health check failed (HTTP ${HTTP_CODE})"
    echo "Please ensure the backend is running: docker compose up -d"
    exit 1
fi
echo ""

echo "=== Step 2: Sending real Zabbix payload ==="
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${WEBHOOK_URL}" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${WEBHOOK_API_KEY}" \
    -d @"${PAYLOAD_FILE}")

HTTP_CODE=$(echo "${RESPONSE}" | tail -n1)
BODY=$(echo "${RESPONSE}" | sed '$d')
echo "HTTP Status: ${HTTP_CODE}"
echo "Response:"
echo "${BODY}" | python3 -m json.tool 2>/dev/null || echo "${BODY}"
echo ""

if [ "${HTTP_CODE}" = "200" ]; then
    echo "=== Webhook received successfully ==="
elif [ "${HTTP_CODE}" = "401" ]; then
    echo "=== ERROR: API Key rejected (check WEBHOOK_API_KEY in .env) ==="
elif [ "${HTTP_CODE}" = "422" ]; then
    echo "=== ERROR: Payload validation failed (check payload format) ==="
else
    echo "=== Unexpected HTTP status: ${HTTP_CODE} ==="
fi
echo ""

echo "=== Step 3: Checking alerts endpoint ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${ALERTS_URL}")
if [ "${HTTP_CODE}" = "200" ]; then
    curl -s "${ALERTS_URL}" | python3 -m json.tool 2>/dev/null
else
    echo "Alerts endpoint returned HTTP ${HTTP_CODE}"
fi
echo ""

echo "=== Test Complete ==="
