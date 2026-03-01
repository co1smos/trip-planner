from typing import Any

from pydantic import BaseModel, Field

class ToolError(BaseModel):
    type: str  # e.g. "VALIDATION_ERROR"|"TIMEOUT"|"TOOL_EXCEPTION"|"NOT_FOUND"|"RATE_LIMIT"
    message: str
    retryable: bool
    details: dict[str, Any] | None

class ToolResult(BaseModel):
    ok: bool
    data: BaseModel | None 
    error: ToolError | None
    meta: dict[str, Any] | None  # e.g execution time, tool version, etc.

class SearchPlacesInput(BaseModel):
    query: str = Field(..., min_length=1)

class EstimateBudgetInput(BaseModel):
    days: int = Field(..., ge=1)
    currency: str
    # total: int

class WeatherHintInput(BaseModel):
    destination: str = Field(..., min_length=1)


class SearchPlacesOutput(BaseModel):
    result: str

class EstimateBudgetOutput(BaseModel):
    total: int

class WeatherHintOutput(BaseModel):
    hint: str

