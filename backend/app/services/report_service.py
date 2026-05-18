from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.alert import Alert
from app.models.ai_analysis import AIAnalysis
from app.models.llm_usage import LLMUsage
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_daily_summary(self, date: str | None = None) -> dict:
        now = datetime.now(timezone.utc)
        start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

        total_alerts_q = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= start)
        )
        total_alerts = total_alerts_q.scalar() or 0

        unresolved_q = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= start, Alert.is_recovery == False)  # noqa: E712
        )
        unresolved = unresolved_q.scalar() or 0

        critical_q = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= start, Alert.severity >= 4)
        )
        critical = critical_q.scalar() or 0

        ai_count_q = await self.db.execute(
            select(func.count(AIAnalysis.id)).where(AIAnalysis.created_at >= start)
        )
        ai_count = ai_count_q.scalar() or 0

        token_usage_q = await self.db.execute(
            select(func.sum(LLMUsage.total_tokens)).where(LLMUsage.created_at >= start)
        )
        token_usage = token_usage_q.scalar() or 0

        llm_calls_q = await self.db.execute(
            select(func.count(LLMUsage.id)).where(LLMUsage.created_at >= start)
        )
        llm_call_count = llm_calls_q.scalar() or 0

        severity_dist_q = await self.db.execute(
            select(Alert.severity_label, func.count(Alert.id))
            .where(Alert.created_at >= start)
            .group_by(Alert.severity_label)
        )
        severity_dist = {row[0]: row[1] for row in severity_dist_q.all()}

        hourly_q = await self.db.execute(
            select(func.extract("hour", Alert.created_at).label("hour"), func.count(Alert.id))
            .where(Alert.created_at >= start)
            .group_by("hour")
            .order_by("hour")
        )
        hourly_trend = [{"hour": int(row[0]), "count": row[1]} for row in hourly_q.all()]

        return {
            "date": date or now.strftime("%Y-%m-%d"),
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved,
            "critical_alerts": critical,
            "ai_analysis_count": ai_count,
            "llm_call_count": llm_call_count,
            "token_usage": token_usage,
            "severity_distribution": severity_dist,
            "hourly_trend": hourly_trend,
        }
