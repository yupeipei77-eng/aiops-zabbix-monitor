import json

import pytest

from app.services.alert_deduplicator import AlertDeduplicator
from app.services.storm_detector import StormDetector


class FakeRedis:
    def __init__(self):
        self.values: dict[str, str | int] = {}
        self.expirations: dict[str, int] = {}

    async def get(self, key: str):
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.values[key] = value
        if ex is not None:
            self.expirations[key] = ex
        return True

    async def incr(self, key: str):
        self.values[key] = int(self.values.get(key, 0)) + 1
        return self.values[key]

    async def expire(self, key: str, seconds: int):
        self.expirations[key] = seconds
        return True


@pytest.mark.asyncio
async def test_deduplicator_records_json_window(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr("app.services.alert_deduplicator.settings.DEDUP_WINDOW_SECONDS", 300)
    deduplicator = AlertDeduplicator(redis_client=fake)

    first_is_dup, first_count = await deduplicator.check_and_record("zabbix:h:t:k")
    second_is_dup, second_count = await deduplicator.check_and_record("zabbix:h:t:k")

    assert first_is_dup is False
    assert first_count == 1
    assert second_is_dup is True
    assert second_count == 2

    stored = json.loads(fake.values["aiops:dedup:zabbix:h:t:k"])
    assert stored["count"] == 2
    assert stored["first_seen"]
    assert stored["last_seen"]
    assert fake.expirations["aiops:dedup:zabbix:h:t:k"] == 300


@pytest.mark.asyncio
async def test_storm_detector_uses_threshold(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr("app.services.storm_detector.settings.STORM_WINDOW_SECONDS", 600)
    monkeypatch.setattr("app.services.storm_detector.settings.STORM_THRESHOLD", 2)
    detector = StormDetector(redis_client=fake)

    assert await detector.check_and_record() is False
    assert await detector.check_and_record() is False
    assert await detector.check_and_record() is True
    assert fake.expirations["aiops:storm:counter"] == 600
