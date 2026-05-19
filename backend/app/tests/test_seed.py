import itertools

import pytest
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import init_db
from app.models.ai_analysis import AIAnalysis
from app.models.alert import Alert
from app.models.base import Base


@pytest.mark.asyncio
async def test_seed_uses_inserted_alert_ids(monkeypatch):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    monkeypatch.setattr(init_db, "async_session_factory", session_factory)

    next_id = itertools.count(101)

    def assign_non_default_id(_mapper, _connection, target):
        if target.id is None:
            target.id = next(next_id)

    event.listen(Alert, "before_insert", assign_non_default_id)
    try:
        await init_db.seed_mock_data()

        async with session_factory() as session:
            alert_ids = set((await session.execute(select(Alert.id))).scalars().all())
            analysis_alert_ids = set((await session.execute(select(AIAnalysis.alert_id))).scalars().all())
    finally:
        event.remove(Alert, "before_insert", assign_non_default_id)
        await engine.dispose()

    assert alert_ids == {101, 102, 103}
    assert analysis_alert_ids == alert_ids
