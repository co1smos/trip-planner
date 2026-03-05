# app/llm/test_client.py
import pytest

import app.llm.client as client_mod
import app.llm.errors as err_mod


class _FakeResp:
    def __init__(self, text: str):
        self.text = text


class _FakeGemini:
    """
    Only the interface we need:
      - generate_content(...) -> object with .text
    """
    def __init__(self, *, text: str | None = None, exc: Exception | None = None):
        self._text = text
        self._exc = exc
        self.calls: list[dict] = []

    def generate_content(self, **kwargs):  # noqa: ANN003
        self.calls.append(kwargs)
        if self._exc is not None:
            raise self._exc
        return _FakeResp(self._text or "")


@pytest.mark.anyio
async def test_parse_constraints_success_returns_dict(monkeypatch):
    """
    Expected behavior (M3.5 plan):
    - LLM returns valid JSON conforming to ParsedConstraints schema
    - parse_constraints returns a dict
    """
    fake = _FakeGemini(text='{"destination":"Tokyo","days":5,"interests":["food"]}')
    monkeypatch.setattr(client_mod, "gemini", fake)

    client = client_mod.get_llm_client()
    out = await client.parse_constraints(query="go tokyo 5 days", constraints_hint=None)

    assert isinstance(out, dict)
    assert out["destination"] == "Tokyo"
    assert out["days"] == 5
    assert out["interests"] == ["food"]

    # sanity: it actually called the LLM once
    assert len(fake.calls) == 1


@pytest.mark.anyio
async def test_parse_constraints_llm_timeout_raises_llmerror(monkeypatch):
    """
    Expected behavior (M3.5 plan):
    - LLM call fails/timeout
    - parse_constraints raises LLMError (plan_node will catch and degrade)
    """
    class Timeout(Exception):
        pass

    fake = _FakeGemini(exc=Timeout("timeout"))
    monkeypatch.setattr(client_mod, "gemini", fake)

    client = client_mod.get_llm_client()

    # We lock the contract to raise LLMError (not return degraded dict here)
    with pytest.raises(err_mod.LLMError):
        await client.parse_constraints(query="x", constraints_hint=None)

    assert len(fake.calls) == 1


@pytest.mark.anyio
async def test_parse_constraints_invalid_json_raises_llmerror(monkeypatch):
    """
    Expected behavior (M3.5 plan):
    - LLM returns non-JSON / invalid JSON
    - parse_constraints raises LLMError
    """
    fake = _FakeGemini(text="NOT JSON")
    monkeypatch.setattr(client_mod, "gemini", fake)

    client = client_mod.get_llm_client()

    with pytest.raises(err_mod.LLMError):
        await client.parse_constraints(query="x", constraints_hint=None)

    assert len(fake.calls) == 1


@pytest.mark.anyio
async def test_parse_constraints_schema_invalid_raises_llmerror(monkeypatch):
    """
    Expected behavior (M3.5 plan):
    - LLM returns JSON that does NOT conform to ParsedConstraints schema
      (e.g., days should be int, but is string)
    - parse_constraints raises LLMError
    """
    fake = _FakeGemini(text='{"destination":"Tokyo","days":"five"}')
    monkeypatch.setattr(client_mod, "gemini", fake)

    client = client_mod.get_llm_client()

    assert hasattr(err_mod, "LLMError"), "Please define LLMError (e.g., in app.llm.errors and re-export/import it)."
    with pytest.raises(err_mod.LLMError):
        await client.parse_constraints(query="x", constraints_hint=None)

    assert len(fake.calls) == 1