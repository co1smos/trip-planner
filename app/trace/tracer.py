import uuid


def new_trace_id() -> str:
    return uuid.uuid4().hex


def log_event(event: dict) -> None:
    print("event:", event)


def span_start(trace_id: str, node: str, payload: dict | None = None) -> None:
    start_event = {
        "trace_id": trace_id,
        "event_type": "START", 
        "node_id": node,
        "payload": payload,
    }
    log_event(start_event)


def span_end(trace_id: str, node: str, payload: dict | None = None) -> None:
    end_event = {
        "trace_id": trace_id,
        "event_type": "END", 
        "node_id": node,
        "payload": payload,
    }
    log_event(end_event)


def span_error(trace_id: str, node: str, err: dict) -> None:
    error_event = {
        "trace_id": trace_id,
        "event_type": "ERROR", 
        "node_id": node,
        "err": err,
    }
    log_event(error_event)