from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.llm import LLMUsageResponse
from app.schemas.common import PaginatedResponse
from app.repositories.usage_repo import UsageRepo
from app.schemas.common import PaginationParams

router = APIRouter()


@router.get("")
async def list_usage(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    params = PaginationParams(page=page, page_size=page_size)
    repo = UsageRepo(db)
    usages, total = await repo.get_list(params)
    return PaginatedResponse(
        data=[LLMUsageResponse.model_validate(u) for u in usages],
        total=total,
        page=page,
        page_size=page_size,
    )
