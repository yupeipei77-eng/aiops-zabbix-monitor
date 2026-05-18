from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.report_service import ReportService
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/daily")
async def daily_report(
    date: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = ReportService(db)
    summary = await service.get_daily_summary(date)
    return ApiResponse(data=summary)


@router.get("/dashboard")
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    from datetime import datetime, timezone
    from app.repositories.alert_repo import AlertRepo
    from app.repositories.ai_analysis_repo import AIAnalysisRepo
    from app.repositories.usage_repo import UsageRepo

    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)

    alert_repo = AlertRepo(db)
    analysis_repo = AIAnalysisRepo(db)
    usage_repo = UsageRepo(db)

    total_alerts = await alert_repo.count_alerts_since(start)
    unresolved = await alert_repo.count_unresolved_since(start)
    critical = await alert_repo.count_critical_since(start)
    ai_count = await analysis_repo.count_since(start)
    token_usage = await usage_repo.total_tokens_since(start)

    return ApiResponse(data={
        "total_alerts": total_alerts,
        "unresolved_alerts": unresolved,
        "critical_alerts": critical,
        "ai_analysis_count": ai_count,
        "token_usage": token_usage,
    })
