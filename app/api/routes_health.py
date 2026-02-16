from fastapi import APIRouter

from app.config import get_settings
from app.store.redis_client import get_redis, check_redis

router = APIRouter()


@router.get("/health")
async def health():
    settings = get_settings()
    r = get_redis(settings)
    ok = await check_redis(r)
    return {
        "ok": bool(ok),
        "redis": "ok" if ok else "down",
    }
