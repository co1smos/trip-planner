from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


RunStatus = Literal["CREATED", "RUNNING", "SUCCEEDED", "FAILED"]


class RunRecord(BaseModel):
    run_id: str
    status: RunStatus
    created_at: int  # epoch seconds
    request: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    state: Dict[str, Any] | None = None
    trace_id: str | None = None 
    last_node: str | None = None
    error: Optional[Dict[str, Any]] = None
