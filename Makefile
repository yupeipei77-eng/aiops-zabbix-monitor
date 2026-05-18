.PHONY: up down logs test backend-test frontend-test migrate seed webhook-test

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test: backend-test frontend-test

backend-test:
	docker compose exec backend pytest -v

frontend-test:
	docker compose exec frontend sh -c "cd /app && npm run build"

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -c "import asyncio; from app.db.init_db import seed_mock_data; asyncio.run(seed_mock_data())"

webhook-test:
	@echo "Sending CPU high alert..."
	@curl -s -X POST http://localhost:8000/api/v1/webhooks/zabbix \
		-H "Content-Type: application/json" \
		-H "X-API-Key: changeme-webhook-api-key" \
		-d @mock/zabbix_payloads/cpu_high.json | python3 -m json.tool
	@echo ""
	@echo "Sending disk full alert..."
	@curl -s -X POST http://localhost:8000/api/v1/webhooks/zabbix \
		-H "Content-Type: application/json" \
		-H "X-API-Key: changeme-webhook-api-key" \
		-d @mock/zabbix_payloads/disk_full.json | python3 -m json.tool
	@echo ""
	@echo "Sending interface down alert..."
	@curl -s -X POST http://localhost:8000/api/v1/webhooks/zabbix \
		-H "Content-Type: application/json" \
		-H "X-API-Key: changeme-webhook-api-key" \
		-d @mock/zabbix_payloads/interface_down.json | python3 -m json.tool
	@echo ""
	@echo "Sending packet loss alert..."
	@curl -s -X POST http://localhost:8000/api/v1/webhooks/zabbix \
		-H "Content-Type: application/json" \
		-H "X-API-Key: changeme-webhook-api-key" \
		-d @mock/zabbix_payloads/packet_loss.json | python3 -m json.tool
