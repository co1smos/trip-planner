import inspect
from redis.asyncio import Redis

from app.config import Settings


def get_redis(settings: Settings) -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def check_redis(r: Redis) -> bool:
    """
    Compatible with redis clients where ping() returns:
    - a coroutine (awaitable), or
    - a plain bool (non-awaitable)
    """
    try:
        res = r.ping()
        if inspect.isawaitable(res):
            res = await res
        return bool(res)
    except Exception:
        return False
