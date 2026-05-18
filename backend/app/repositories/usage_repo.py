from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.llm_usage import LLMUsage
from app.schemas.common import PaginationParams


class UsageRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, params: PaginationParams) -> tuple[list[LLMUsage], int]:
        query = select(LLMUsage).order_by(LLMUsage.created_at.desc())
        total_result = await self.db.execute(select(func.count(LLMUsage.id)))
        total = total_result.scalar() or 0

        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)
        result = await self.db.execute(query)
        usages = list(result.scalars().all())

        return usages, total

    async def create(self, **kwargs) -> LLMUsage:
        usage = LLMUsage(**kwargs)
        self.db.add(usage)
        await self.db.flush()
        return usage

    async def total_tokens_since(self, since) -> int:
        result = await self.db.execute(
            select(func.sum(LLMUsage.total_tokens)).where(LLMUsage.created_at >= since)
        )
        return result.scalar() or 0
