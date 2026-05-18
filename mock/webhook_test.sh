#!/bin/bash
set -euo pipefail

API_KEY="${WEBHOOK_API_KEY:-changeme-webhook-api-key}"
BASE_URL="${BASE_URL:-http://localhost:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PAYLOAD_DIR="${SCRIPT_DIR}/zabbix_payloads"

pretty_get() {
  curl -fsS "$1" | python3 -m json.tool
}

post_payload() {
  local payload_file="$1"
  curl -fsS -X POST "${BASE_URL}/api/v1/webhooks/zabbix" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${API_KEY}" \
    -d @"${PAYLOAD_DIR}/${payload_file}" | python3 -m json.tool
}

echo "=== AIOps Zabbix Monitor - Webhook Test ==="
echo ""

echo "1. Health Check..."
pretty_get "${BASE_URL}/api/v1/health"
echo ""

echo "2. Sending CPU high alert..."
post_payload "cpu_high.json"
echo ""

echo "3. Sending disk full alert..."
post_payload "disk_full.json"
echo ""

echo "4. Sending interface down alert..."
post_payload "interface_down.json"
echo ""

echo "5. Sending packet loss alert..."
post_payload "packet_loss.json"
echo ""

echo "6. Listing alerts..."
pretty_get "${BASE_URL}/api/v1/alerts"
echo ""

echo "7. Triggering AI analysis for alert #1..."
curl -fsS -X POST "${BASE_URL}/api/v1/ai/1/analyze" \
  -H "Content-Type: application/json" | python3 -m json.tool
echo ""

echo "=== Test Complete ==="
