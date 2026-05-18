from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.alert import Alert
from app.schemas.alert import AlertListParams


class AlertRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, alert_id: int) -> Alert | None:
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalars().first()

    async def get_list(self, params: AlertListParams) -> tuple[list[Alert], int]:
        query = select(Alert)
        count_query = select(func.count(Alert.id))

        if params.severity is not None:
            query = query.where(Alert.severity == params.severity)
            count_query = count_query.where(Alert.severity == params.severity)
        if params.host_name:
            query = query.where(Alert.host_name.ilike(f"%{params.host_name}%"))
            count_query = count_query.where(Alert.host_name.ilike(f"%{params.host_name}%"))

        query = query.order_by(Alert.created_at.desc())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (params.page - 1) * params.page_size
        query = query.offset(offset).limit(params.page_size)
        result = await self.db.execute(query)
        alerts = list(result.scalars().all())

        return alerts, total

    async def create(self, **kwargs) -> Alert:
        alert = Alert(**kwargs)
        self.db.add(alert)
        await self.db.flush()
        return alert

    async def update_dedup_count(self, alert_id: int, count: int) -> None:
        alert = await self.get_by_id(alert_id)
        if alert:
            alert.dedup_count = count
            await self.db.flush()

    async def get_recent_alerts(self, limit: int = 20) -> list[Alert]:
        result = await self.db.execute(
            select(Alert).order_by(Alert.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def count_alerts_since(self, since) -> int:
        result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= since)
        )
        return result.scalar() or 0

    async def count_unresolved_since(self, since) -> int:
        result = await self.db.execute(
            select(func.count(Alert.id)).where(
                Alert.created_at >= since, Alert.is_recovery == False  # noqa: E712
            )
        )
        return result.scalar() or 0

    async def count_critical_since(self, since) -> int:
        result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.created_at >= since, Alert.severity >= 4)
        )
        return result.scalar() or 0
