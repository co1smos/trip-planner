from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel


RunStatus = Literal["CREATED", "RUNNING", "SUCCEEDED", "FAILED"]


class RunRecord(BaseModel):
    run_id: str
    status: RunStatus
    created_at: int  # epoch seconds
    request: dict[str, Any]
    result: dict[str, Any] | None = None
    errors: dict[str, Any] | None = None
