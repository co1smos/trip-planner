from app.trace.tracer import (
    new_trace_id,
    log_event,
    span_start,
    span_end,
    span_error,
)

def test_tracer_helpers_and_log_event(monkeypatch):
    # ensure new_trace_id works
    tid1 = new_trace_id()
    tid2 = new_trace_id()
    assert tid1 and tid2 and tid1 != tid2

    # capture output if log_event prints to stdout
    printed = {"calls": 0}

    def _fake_print(*args, **kwargs):
        printed["calls"] += 1
        # If your log_event prints JSON, this keeps it exercised without strict coupling.
        if args:
            _ = str(args[0])

    monkeypatch.setattr("builtins.print", _fake_print)

    # call log_event directly (coverage for this function)
    log_event({"trace_id": tid1, "event": "test", "x": 1})
    assert printed["calls"] >= 1

    # span wrappers should also call log_event internally (or at least not throw)
    span_start(tid1, "n1", {"a": 1})
    span_end(tid1, "n1", {"ok": True})
    span_error(tid1, "n1", {"type": "X", "msg": "oops"})
