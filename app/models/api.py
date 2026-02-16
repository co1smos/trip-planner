from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PlanTripRequest(BaseModel):
    """
    API request model (M0):
    - query: natural language input
    - constraints: optional dict (kept flexible in M0)
    - client_request_id: optional (reserved for future idempotency; not used in M0)
    """
    query: str = Field(..., min_length=1, description="User's natural language travel request")
    constraints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional structured constraints (flexible dict in M0)"
    )
    client_request_id: Optional[str] = Field(
        default=None,
        description="Optional client-supplied request id (reserved for future use)"
    )


class PlanTripResponse(BaseModel):
    """
    API response for POST /plan_trip (M0):
    - run_id: server-generated identifier
    - status: CREATED (M0)
    """
    run_id: str
    status: str


class GetRunResponse(BaseModel):
    """
    API response for GET /runs/{run_id} (M0):
    Return whatever we stored for this run.
    """
    run_id: str
    status: str
    created_at: int
    request: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
