import asyncio
import pytest
from pydantic import BaseModel, Field

from app.models.tools import ToolResult
from app.tools.registry import ToolRegistry, build_registry


class _In(BaseModel):
    q: str = Field(..., min_length=1)


class _Out(BaseModel):
    echo: str


async def _ok_tool(inp: _In) -> ToolResult:
    return ToolResult(ok=True, data=_Out(echo=inp.q), error=None, meta=None)


async def _boom_tool(inp: _In) -> ToolResult:
    raise RuntimeError("boom")


async def _slow_tool(inp: _In) -> ToolResult:
    await asyncio.sleep(0.2)
    return ToolResult(ok=True, data=_Out(echo=inp.q), error=None, meta=None)


def _make_registry() -> ToolRegistry:
    reg = ToolRegistry()
    # assume registry supports output_model registration (recommended). If you ignore it, tests still pass.
    reg.register("ok", _ok_tool, _In, _Out)
    reg.register("boom", _boom_tool, _In, _Out)
    reg.register("slow", _slow_tool, _In, _Out)
    return reg


@pytest.mark.anyio
async def test_registry_success_call_returns_ok_and_output_model():
    reg = _make_registry()
    res = await reg.call("ok", {"q": "hi"}, timeout_s=1.0)
    assert res.ok is True
    assert res.error is None
    # scalable: data is typed model
    assert isinstance(res.data, _Out)
    assert res.data.echo == "hi"


@pytest.mark.anyio
async def test_registry_unknown_tool_returns_not_found():
    reg = _make_registry()
    res = await reg.call("missing", {"q": "hi"}, timeout_s=1.0)
    assert res.ok is False
    assert res.data is None
    assert res.error is not None
    assert res.error.type == "NOT_FOUND"
    assert isinstance(res.error.message, str)


@pytest.mark.anyio
async def test_registry_validation_error_returns_validation_error():
    reg = _make_registry()
    res = await reg.call("ok", {}, timeout_s=1.0)  # missing q
    assert res.ok is False
    assert res.data is None
    assert res.error is not None
    assert res.error.type == "VALIDATION_ERROR"
    assert res.error.details is None or isinstance(res.error.details, dict)


@pytest.mark.anyio
async def test_registry_tool_exception_returns_tool_exception():
    reg = _make_registry()
    res = await reg.call("boom", {"q": "x"}, timeout_s=1.0)
    assert res.ok is False
    assert res.data is None
    assert res.error is not None
    assert res.error.type == "TOOL_EXCEPTION"
    assert isinstance(res.error.message, str)
    assert "boom" in res.error.message.lower()


@pytest.mark.anyio
async def test_registry_timeout_returns_timeout():
    reg = _make_registry()
    res = await reg.call("slow", {"q": "x"}, timeout_s=0.01)
    assert res.ok is False
    assert res.data is None
    assert res.error is not None
    assert res.error.type == "TOOL_EXCEPTION"
    assert "timeout" in res.error.message.lower()
    assert isinstance(res.error.retryable, bool)


def test_build_registry_registers_tools():
    reg = build_registry()
    names = reg.list_tools()
    assert isinstance(names, list)
    assert len(names) >= 1
    # 你若按推荐命名，可加更严格断言：
    # assert "search_places" in names
    # assert "estimate_budget" in names