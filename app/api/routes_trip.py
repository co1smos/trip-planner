from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.api import PlanTripRequest, PlanTripResponse, GetRunResponse
from app.store.redis_client import get_redis
from app.store.run_store import RunStore

router = APIRouter(prefix="", tags=["trip"])


@router.post("/plan_trip", response_model=PlanTripResponse)
async def plan_trip(req: PlanTripRequest):
    """
    M0 behavior:
    - Accept query + optional constraints
    - Create a run record in Redis with status=CREATED
    - Return run_id + status (no itinerary generation in M0)
    """
    settings = get_settings()
    r = get_redis(settings)
    store = RunStore(r, ttl_s=settings.RUN_TTL_S)

    record = await store.create_run(request_dict=req.model_dump())
    return PlanTripResponse(run_id=record.run_id, status=record.status)


@router.get("/runs/{run_id}", response_model=GetRunResponse)
async def get_run(run_id: str):
    settings = get_settings()
    r = get_redis(settings)
    store = RunStore(r, ttl_s=settings.RUN_TTL_S)

    record = await store.load_run(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")

    return GetRunResponse(
        run_id=record.run_id,
        status=record.status,
        created_at=record.created_at,
        request=record.request,
        result=record.result,
        error=record.error,
    )
