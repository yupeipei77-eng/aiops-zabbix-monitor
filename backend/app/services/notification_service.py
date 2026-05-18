from app.core.logging import get_logger

logger = get_logger(__name__)


class NotificationService:
    @staticmethod
    async def send_alert_notification(alert_data: dict, analysis_data: dict | None = None) -> None:
        logger.info(
            "Notification: alert=%s, host=%s, severity=%s",
            alert_data.get("event_id"),
            alert_data.get("host_name"),
            alert_data.get("severity_label"),
        )

    @staticmethod
    async def send_storm_notification(count: int) -> None:
        logger.warning("Storm notification: %d alerts in window", count)
