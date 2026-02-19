from app.trace.tracer import new_trace_id, span_start, span_end, span_error


def test_tracer_helpers():
    tid1 = new_trace_id()
    tid2 = new_trace_id()
    assert tid1 and tid2 and tid1 != tid2

    span_start(tid1, "n1", {"a": 1})
    span_end(tid1, "n1", {"ok": True})
    span_error(tid1, "n1", {"type": "X", "msg": "oops"})
