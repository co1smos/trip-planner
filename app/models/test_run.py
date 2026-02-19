from app.models.run import RunRecord


def test_run_record_defaults_and_optionals():
    r = RunRecord(
        run_id="1",
        status="CREATED",
        created_at=0,
        request={"query": "x"},
    )

    # existing defaults
    assert r.result is None
    assert r.error is None

    # M1 optionals MUST default to None
    assert r.trace_id is None
    assert r.last_node is None
    assert r.state is None

    # explicit values should be accepted
    r2 = RunRecord(
        run_id="2",
        status="SUCCEEDED",
        created_at=1,
        request={"query": "y"},
        trace_id="tid",
        last_node="synthesize",
        state={"k": "v"},
        result={"message": "ok"},
    )
    
    assert r2.trace_id == "tid"
    assert r2.last_node == "synthesize"
    assert r2.state["k"] == "v"
    assert r2.result["message"] == "ok"
