import pytest

from app.models.tools import ToolError, ToolResult


def test_tool_result_ok_shape():
    r = ToolResult(ok=True, data=None, error=None, meta={"ms": 1})
    assert r.ok is True
    assert r.error is None
    assert r.meta == {"ms": 1}


def test_tool_result_error_shape():
    e = ToolError(type="TIMEOUT", message="t", retryable=True, details={"a": 1})
    r = ToolResult(ok=False, data=None, error=e, meta=None)
    assert r.ok is False
    assert r.data is None
    assert r.error is not None
    assert r.error.type == "TIMEOUT"
    assert isinstance(r.error.retryable, bool)
    assert r.error.details == {"a": 1}


def test_tool_error_minimum_fields():
    e = ToolError(type="TOOL_EXCEPTION", message="boom", retryable=False, details=None)
    assert e.type == "TOOL_EXCEPTION"
    assert e.message == "boom"
    assert e.retryable is False
    assert e.details is None