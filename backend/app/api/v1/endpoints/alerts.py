from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.alert import AlertResponse, AlertListParams
from app.schemas.common import ApiResponse, PaginatedResponse
from app.repositories.alert_repo import AlertRepo
from app.services.model_router import ModelRouter
from typing import Optional

router = APIRouter()


def _alert_response_with_ai_policy(alert) -> AlertResponse:
    response = AlertResponse.model_validate(alert)
    should_analyze, reason = ModelRouter.should_analyze(alert.severity)
    response.ai_analysis_enabled = should_analyze
    response.ai_skip_reason = reason
    return response


@router.get("")
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[int] = Query(None),
    host_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    params = AlertListParams(page=page, page_size=page_size, severity=severity, host_name=host_name)
    repo = AlertRepo(db)
    alerts, total = await repo.get_list(params)
    return PaginatedResponse(
        data=[_alert_response_with_ai_policy(a) for a in alerts],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{alert_id}")
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    repo = AlertRepo(db)
    alert = await repo.get_by_id(alert_id)
    if not alert:
        return ApiResponse(success=False, data=None, message="Alert not found")
    return ApiResponse(data=_alert_response_with_ai_policy(alert))
