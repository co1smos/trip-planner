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
    assert r.errors is None

    # explicit values should be accepted
    r2 = RunRecord(
        run_id="2",
        status="SUCCEEDED",
        created_at=1,
        request={"query": "y"},
        result={"message": "ok"},
    )
    
    assert r2.result["message"] == "ok"
