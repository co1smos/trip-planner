from app.config import Settings
from app.store.redis_client import check_redis, get_redis
from app.store._test_fakes import FakeRedis


def test_get_redis_builds_client():
    s = Settings(REDIS_URL="redis://localhost:6379/0", RUN_TTL_S=1)
    r = get_redis(s)
    # smoke: object exists
    assert r is not None


async def test_check_redis_ok():
    r = FakeRedis(ping_ok=True)
    assert await check_redis(r) is True


async def test_check_redis_down():
    r = FakeRedis(ping_ok=False)
    assert await check_redis(r) is False
