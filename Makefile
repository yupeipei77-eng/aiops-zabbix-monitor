.PHONY: up down logs build test backend-test frontend-test migrate seed webhook-test

up:
	docker compose up -d

build:
	docker compose build

down:
	docker compose down

logs:
	docker compose logs -f

test: backend-test frontend-test

backend-test:
	docker compose exec -T backend pytest -q

frontend-test:
	docker compose --profile test run --rm frontend-test

migrate:
	docker compose exec -T backend alembic upgrade head

seed:
	docker compose exec -T backend python -c "import asyncio; from app.db.init_db import seed_mock_data; asyncio.run(seed_mock_data())"

webhook-test:
	./mock/webhook_test.sh
