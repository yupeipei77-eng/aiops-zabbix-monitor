from fastapi import APIRouter
from app.api.v1.endpoints import health, zabbix_webhook, alerts, ai_analysis, llm_usage, knowledge, reports

router = APIRouter(prefix="/api/v1")

router.include_router(health.router, prefix="/health", tags=["health"])
router.include_router(zabbix_webhook.router, prefix="/webhooks/zabbix", tags=["webhooks"])
router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
router.include_router(ai_analysis.router, prefix="/ai", tags=["ai"])
router.include_router(llm_usage.router, prefix="/llm", tags=["llm"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
router.include_router(reports.router, prefix="/reports", tags=["reports"])
