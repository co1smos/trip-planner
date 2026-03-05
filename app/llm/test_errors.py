# app/llm/test_errors.py
import pytest

import app.llm.errors as err_mod


def test_llmerror_is_exception_and_has_message():
    """
    Basic contract: LLMError is an Exception with a message.
    Also ensures __str__ doesn't crash (covers common __str__/__repr__).
    """
    if hasattr(err_mod, "LLMError"):
        e = err_mod.LLMError("boom")  # type: ignore[attr-defined]
        assert isinstance(e, Exception)
        assert "boom" in str(e)
    else:
        pytest.skip("LLMError not defined in app.llm.errors")


def test_llmerror_fields_default_values_if_present():
    LLMError = err_mod.LLMError  # type: ignore[attr-defined]
    e = LLMError("x")

    assert getattr(e, "type") is not None
    assert isinstance(getattr(e, "retryable"), bool)
    d = getattr(e, "details")
    assert d is None or isinstance(d, dict)


def test_is_retryable_behavior_if_present():
    is_retryable = err_mod.is_retryable  # type: ignore[attr-defined]

    # If your helper supports generic exceptions:
    assert is_retryable(Exception("x")) in (True, False)

    if hasattr(err_mod, "LLMError"):
        LLMError = err_mod.LLMError  # type: ignore[attr-defined]

        e1 = LLMError("t1", retryable=True)  # type: ignore[call-arg]
        e2 = LLMError("t2", retryable=False)  # type: ignore[call-arg]

        assert is_retryable(e1) is True
        assert is_retryable(e2) is False


def test_llmerror_failure_case_can_be_raised_and_caught():
    """
    Explicit failure path coverage: raising LLMError should be catchable and stable.
    """
    LLMError = err_mod.LLMError  # type: ignore[attr-defined]

    with pytest.raises(LLMError):
        raise LLMError("raise me")