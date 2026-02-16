from app.models.run import RunRecord


def test_run_record_defaults():
    r = RunRecord(run_id="1", status="CREATED", created_at=0, request={"query": "x"})
    assert r.result is None
    assert r.error is None
