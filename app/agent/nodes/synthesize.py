from app.models.state import AgentState, summarize_state
from app.trace.tracer import span_start, span_end

from typing import Any, Dict, List, Optional

NODE_ID = "synthesize"

def _safe_get(d: Any, path: List[str], default: Any = None) -> Any:
    """Safely get nested keys from a dict-like object."""
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def _extract_budget(observations: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """
    Extract budget info from estimate_budget ToolResult.
    We expect observations entries like:
      { "tool": "estimate_budget", "result": { "ok": bool, "data": {...}, "error": {...}} }
    """
    for ob in observations:
        if ob.get("tool") != "estimate_budget":
            continue
        result = ob.get("result") or {}
        if not isinstance(result, dict):
            continue
        if result.get("ok") is not True:
            return None
        data = result.get("data")
        if isinstance(data, dict):
            # keep full tool data; caller can render however it wants
            return data
    return None


def _extract_places(observations: list[dict[str, Any]]) -> List[dict[str, Any]]:
    """
    Extract places from search_places ToolResult.
    Expected tool data:
      result.data.places = [ {name: ...}, ... ]
    """
    for ob in observations:
        if ob.get("tool") != "search_places":
            continue
        result = ob.get("result") or {}
        if not isinstance(result, dict) or result.get("ok") is not True:
            return []
        places = _safe_get(result, ["data", "places"], default=[])
        if isinstance(places, list):
            return [p for p in places if isinstance(p, dict)]
        return []
    return []


def _notes_from_errors(errors: List[Dict[str, Any]]) -> List[str]:
    notes: List[str] = []
    for e in errors:
        if not isinstance(e, dict):
            continue
        et = e.get("type") or e.get("code") or "error"
        msg = e.get("message") or e.get("detail") or ""
        if msg:
            notes.append(f"{et}: {msg}")
        else:
            notes.append(str(et))
    return notes


def _notes_from_tool_failures(observations: List[Dict[str, Any]]) -> List[str]:
    notes: List[str] = []
    for ob in observations:
        tool = ob.get("tool")
        result = ob.get("result") or {}
        if not isinstance(tool, str) or not isinstance(result, dict):
            continue
        if result.get("ok") is True:
            continue
        err_type = _safe_get(result, ["error", "type"], default="TOOL_ERROR")
        err_msg = _safe_get(result, ["error", "message"], default="tool call failed")
        notes.append(f"{tool} failed ({err_type}): {err_msg}")
    return notes


def _build_itinerary_preview(
    *,
    days: Optional[int],
    destination: Optional[str],
    places: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Deterministic itinerary preview builder:
    - If days is missing, default to 2 for preview
    - Use up to (days * 2) place suggestions, 2 per day
    """
    preview_days = days if isinstance(days, int) and days > 0 else 2
    preview_days = min(preview_days, 7)  # keep preview bounded / stable

    # Select place names deterministically in input order
    names = [p.get("name") for p in places if isinstance(p.get("name"), str)]
    # 2 spots per day
    target = preview_days * 2
    names = names[:target]

    itinerary: List[Dict[str, Any]] = []
    idx = 0
    for d in range(1, preview_days + 1):
        day_spots = names[idx : idx + 2]
        idx += 2
        itinerary.append(
            {
                "day": d,
                "destination": destination,
                "spots": day_spots,
                "note": "auto-generated preview (deterministic)",
            }
        )
    return itinerary

# Post Processing Layer
async def synthesize_node(state: AgentState) -> AgentState:
    """
    M3.5 synthesize:
    - Consume tool observations + state.errors
    - Build stable result dict:
        {
          "summary": str,
          "tools_used": [..],
          "budget": {...} | null,
          "itinerary_preview": [...],
          "notes": [...],
          "meta": {...}
        }
    - Never raise (should not 500). Degrade gracefully.
    """
    span_start(state.trace_id, NODE_ID, summarize_state(state))
    tools_used = [obs.get("tool") for obs in state.observations if "tool" in obs]
    tools_error = [obs.get("result", {}).get("error") for obs in state.observations if obs.get('result', {}).get('ok') is False]

    budget = _extract_budget(state.observations)
    places = _extract_places(state.observations)

    request = getattr(state, "request", {}) if isinstance(getattr(state, "request", {}), dict) else {}
    constraints = request.get("constraints") if isinstance(request, dict) else None
    constraints = constraints if isinstance(constraints, dict) else {}

    destination = constraints.get("destination")
    if not isinstance(destination, str):
        destination = None

    days = constraints.get("days")
    if not isinstance(days, int):
        days = None

    itinerary_preview = _build_itinerary_preview(days=days, destination=destination, places=places)

    notes: List[str] = []
    notes.extend(_notes_from_errors(tools_error))
    notes.extend(_notes_from_tool_failures(state.observations))
    if not tools_used:
        notes.append("no tools executed; result is minimal")

    state.result = {
        "result": "finished", 
        "tools_used": tools_used, 
        "tools_error": tools_error,
        "budget": budget,
        "notes": notes,
        "itinerary_preview": itinerary_preview,
        "meta": {
            "observations_count": len(state.observations),
            "errors_count": len(state.errors),
        },
    }
    state.last_node = NODE_ID
    span_end(state.trace_id, NODE_ID, summarize_state(state))
    return state