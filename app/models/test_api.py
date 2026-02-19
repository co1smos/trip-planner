import pytest
from pydantic import ValidationError

from app.models.api import PlanTripRequest, PlanTripResponse, GetRunResponse


def test_plan_trip_request_minimal():
    req = PlanTripRequest(query="hello")
    assert req.query == "hello"
    assert req.constraints is None
    assert req.client_request_id is None


def test_plan_trip_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        PlanTripRequest(query="")  # min_length=1


def test_api_responses_construct():
    r1 = PlanTripResponse(run_id="abc", status="CREATED")
    assert r1.run_id == "abc"

    r2 = GetRunResponse(
        run_id="abc",
        status="CREATED",
        created_at=1,
        request={"query": "x"},
        result=None,
        error=None,
    )
    assert r2.request["query"] == "x"


def test_get_run_response_requires_state_summary():
    obj = GetRunResponse(
        run_id="rid",
        status="SUCCEEDED",
        created_at=1,
        request={"query": "x", "constraints": None},
        result={"message": "ok"},
        error=None,
        state_summary={
            "run_id": "rid",
            "last_node": "synthesize",
            "plan_steps_count": 1,
            "observations_count": 1,
        },
    )
    assert obj.state_summary["last_node"] == "synthesize"