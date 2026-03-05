# app/llm/test_schemas.py
import pytest
from pydantic import ValidationError

from app.llm.schemas import ParsedConstraints, merge_constraints


def test_parsed_constraints_validation_days_positive():
    # days <= 0 should fail validation if provided
    with pytest.raises(ValidationError):
        ParsedConstraints(days=0)
    with pytest.raises(ValidationError):
        ParsedConstraints(days=-3)

    # None is allowed
    pc = ParsedConstraints(days=None)
    assert pc.days is None

    # positive ok
    pc2 = ParsedConstraints(days=3)
    assert pc2.days == 3


def test_merge_constraints_handles_none_inputs():
    parsed = ParsedConstraints(destination="Tokyo", days=5)
    out = merge_constraints(None, parsed)
    assert isinstance(out, dict)
    assert out.get("destination") == "Tokyo"
    assert out.get("days") == 5

    out2 = merge_constraints({"days": 7}, ParsedConstraints())
    assert out2.get("days") == 7


def test_merge_constraints_prefers_api_or_parsed_as_specified():
    """
    This test locks your merge priority.
    If you decide API constraints should override parsed results (recommended),
    then this should pass as written.

    If your implementation prefers parsed over API, flip the expectations.
    """
    api = {"destination": "Kyoto", "days": 7, "budget": {"currency": "USD", "total": 1000}}
    parsed = ParsedConstraints(destination="Tokyo", days=5, budget={"currency": "USD", "total": 2000})

    out = merge_constraints(api, parsed)

    # Expect API wins (adjust if you chose the opposite rule)
    assert out["destination"] == "Kyoto"
    assert out["days"] == 7
    assert out["budget"]["total"] == 1000