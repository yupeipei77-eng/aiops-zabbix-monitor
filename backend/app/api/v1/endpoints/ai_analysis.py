from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.ai_analysis import AIAnalysisResponse, AIAnalysisRequest
from app.schemas.common import ApiResponse, PaginatedResponse
from app.repositories.ai_analysis_repo import AIAnalysisRepo
from app.services.ai_orchestrator import AIOrchestrator

router = APIRouter()


@router.get("")
async def list_analyses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    from app.schemas.common import PaginationParams
    params = PaginationParams(page=page, page_size=page_size)
    repo = AIAnalysisRepo(db)
    analyses, total = await repo.get_list(params)
    return PaginatedResponse(
        data=[AIAnalysisResponse.model_validate(a) for a in analyses],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/alerts/{alert_id}")
async def get_analysis_by_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    repo = AIAnalysisRepo(db)
    analysis = await repo.get_by_alert_id(alert_id)
    if not analysis:
        return ApiResponse(success=False, data=None, message="AI analysis not found")
    return ApiResponse(data=AIAnalysisResponse.model_validate(analysis))


@router.post("/{alert_id}/analyze")
async def analyze_alert(
    alert_id: int,
    body: AIAnalysisRequest | None = None,
    db: AsyncSession = Depends(get_db),
):
    orchestrator = AIOrchestrator(db)
    result = await orchestrator.analyze_alert(
        alert_id,
        preferred_provider=body.provider if body else None,
        preferred_model=body.model if body else None,
        force=body.force if body else False,
    )
    if not result["success"]:
        return ApiResponse(success=False, data=None, message=result["message"])
    return ApiResponse(data=result["data"])
