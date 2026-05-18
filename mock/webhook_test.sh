#!/bin/bash
set -e

API_KEY="${WEBHOOK_API_KEY:-changeme-webhook-api-key}"
BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "=== AIOps Zabbix Monitor - Webhook Test ==="
echo ""

echo "1. Health Check..."
curl -s "${BASE_URL}/api/v1/health" | python3 -m json.tool
echo ""

echo "2. Sending CPU high alert..."
curl -s -X POST "${BASE_URL}/api/v1/webhooks/zabbix" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d @mock/zabbix_payloads/cpu_high.json | python3 -m json.tool
echo ""

echo "3. Sending disk full alert..."
curl -s -X POST "${BASE_URL}/api/v1/webhooks/zabbix" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d @mock/zabbix_payloads/disk_full.json | python3 -m json.tool
echo ""

echo "4. Sending interface down alert..."
curl -s -X POST "${BASE_URL}/api/v1/webhooks/zabbix" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d @mock/zabbix_payloads/interface_down.json | python3 -m json.tool
echo ""

echo "5. Sending packet loss alert..."
curl -s -X POST "${BASE_URL}/api/v1/webhooks/zabbix" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d @mock/zabbix_payloads/packet_loss.json | python3 -m json.tool
echo ""

echo "6. Listing alerts..."
curl -s "${BASE_URL}/api/v1/alerts" | python3 -m json.tool
echo ""

echo "7. Triggering AI analysis for alert #1..."
curl -s -X POST "${BASE_URL}/api/v1/ai/1/analyze" \
  -H "Content-Type: application/json" | python3 -m json.tool
echo ""

echo "=== Test Complete ==="
