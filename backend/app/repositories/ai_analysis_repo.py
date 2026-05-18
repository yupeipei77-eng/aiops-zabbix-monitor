from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.ai_analysis import AIAnalysis
from app.schemas.common import PaginationParams


class AIAnalysisRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_alert_id(self, alert_id: int) -> AIAnalysis | None:
        result = await self.db.execute(select(AIAnalysis).where(AIAnalysis.alert_id == alert_id))
        return result.scalars().first()

    async def get_list(self, params: PaginationParams) -> tuple[list[AIAnalysis], int]:
        query = select(AIAnalysis).order_by(AIAnalysis.created_at.desc())
        total_result = await self.db.execute(select(func.count(AIAnalysis.id)))
        total = total_result.scalar() or 0

        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)
        result = await self.db.execute(query)
        analyses = list(result.scalars().all())

        return analyses, total

    async def create(self, **kwargs) -> AIAnalysis:
        analysis = AIAnalysis(**kwargs)
        self.db.add(analysis)
        await self.db.flush()
        return analysis

    async def count_since(self, since) -> int:
        result = await self.db.execute(
            select(func.count(AIAnalysis.id)).where(AIAnalysis.created_at >= since)
        )
        return result.scalar() or 0
