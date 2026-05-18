from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.zabbix import ZabbixWebhookPayload
from app.schemas.common import ApiResponse
from app.services.alert_normalizer import AlertNormalizer
from app.services.alert_deduplicator import AlertDeduplicator
from app.services.storm_detector import StormDetector
from app.services.ai_orchestrator import AIOrchestrator
from app.repositories.alert_repo import AlertRepo
from app.core.security import verify_api_key
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

deduplicator = AlertDeduplicator()
storm_detector = StormDetector()


@router.post("")
async def receive_zabbix_webhook(
    payload: ZabbixWebhookPayload,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    normalized = AlertNormalizer.normalize(payload)

    is_storm = await storm_detector.check_and_record()
    if is_storm:
        normalized["storm_detected"] = True

    alert_repo = AlertRepo(db)
    alert = await alert_repo.create(**normalized)

    is_dup, count = await deduplicator.check_and_record(normalized["dedup_key"])
    if is_dup:
        await alert_repo.update_dedup_count(alert.id, count)
        logger.info("Duplicate alert: dedup_key=%s, count=%d", normalized["dedup_key"], count)
        return ApiResponse(
            success=True,
            data={"alert_id": alert.id, "is_duplicate": True, "dedup_count": count},
            message="Duplicate alert recorded",
        )

    if not is_storm:
        orchestrator = AIOrchestrator(db)
        try:
            result = await orchestrator.analyze_alert(alert.id)
            logger.info("AI analysis completed for alert %d", alert.id)
        except Exception as e:
            logger.error("AI analysis failed for alert %d: %s", alert.id, str(e))

    return ApiResponse(
        success=True,
        data={"alert_id": alert.id, "is_duplicate": False, "storm_detected": is_storm},
        message="Alert accepted",
    )
