
from pydantic import BaseModel, Field


class ParsedConstraints(BaseModel):
    days: int | None = Field(default=None, ge=1)
    destination: str | None = Field(default=None)
    date_range: dict | None = Field(default=None)
    budget: dict | None = Field(default=None)
    interests: list[str] | None = Field(default=None)
    style: str | None = Field(default=None)
    pace: str | None = Field(default=None)
    limit: int | None = Field(default=None)

def merge_constraints(api_constraints: dict | None, parsed: ParsedConstraints) -> dict:
    """
    Merge API constraints and parsed constraints into a single dict.
    Priority rules:
    - For simple fields (destination, days, style, pace): API > Parsed
    - For dict fields (date_range, budget): deep merge with API taking precedence
    - For list fields (interests): API if provided, else parsed
    - For limit: API > Parsed
    """
    merged = {}

    # Simple fields
    for field in ["destination", "days", "style", "pace"]:
        merged[field] = api_constraints.get(field) if api_constraints and field in api_constraints else getattr(parsed, field)

    # Dict fields with deep merge
    for field in ["date_range", "budget"]:
        api_value = api_constraints.get(field) if api_constraints and field in api_constraints else None
        parsed_value = getattr(parsed, field)
        if isinstance(api_value, dict) and isinstance(parsed_value, dict):
            merged[field] = {**parsed_value, **api_value}  # API takes precedence
        else:
            merged[field] = api_value or parsed_value

    # List fields
    merged["interests"] = api_constraints.get("interests") if api_constraints and "interests" in api_constraints else parsed.interests

    # Limit
    merged["limit"] = api_constraints.get("limit") if api_constraints and "limit" in api_constraints else parsed.limit

    return merged