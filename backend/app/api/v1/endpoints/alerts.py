from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.alert import AlertResponse, AlertListParams
from app.schemas.common import ApiResponse, PaginatedResponse
from app.repositories.alert_repo import AlertRepo
from typing import Optional

router = APIRouter()


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
        data=[AlertResponse.model_validate(a) for a in alerts],
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
    return ApiResponse(data=AlertResponse.model_validate(alert))
