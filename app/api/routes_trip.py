from fastapi import APIRouter, HTTPException

from app.agent.runner import WorkflowRunner
from app.config import get_settings
from app.models.api import PlanTripRequest, PlanTripResponse, GetRunResponse
from app.models.state import summarize_state
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
    runner = WorkflowRunner(store)

    record = await store.create_run(request_dict=req.model_dump())
    _ = await runner.run_workflow(record.run_id)  # fire and forget
    record = await store.load_run(record.run_id)  # reload to get updated status/result
    return PlanTripResponse(run_id=record.run_id, status=record.status)


@router.get("/runs/{run_id}", response_model=GetRunResponse)
async def get_run(run_id: str):
    settings = get_settings()
    r = get_redis(settings)
    store = RunStore(r, ttl_s=settings.RUN_TTL_S)

    record = await store.load_run(run_id)
    state = await store.load_state(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    if state is None:
        raise HTTPException(status_code=404, detail="state not found")

    return GetRunResponse(
        run_id=record.run_id,
        status=record.status,
        created_at=record.created_at,
        request=record.request,
        state_summary=summarize_state(state),
        result=record.result,
        error=record.errors,
    )
