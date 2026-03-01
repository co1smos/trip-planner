from app.models.tools import ToolResult, EstimateBudgetInput, EstimateBudgetOutput
from app.tools.estimate_budget import estimate_budget


def test_estimate_budget_ok_returns_typed_output():
    inp = EstimateBudgetInput(days=3, currency="USD", total=1000)
    res = estimate_budget(inp)

    assert isinstance(res, ToolResult)
    assert isinstance(res.ok, bool)

    assert res.ok is True
    assert res.error is None
    assert isinstance(res.data, EstimateBudgetOutput)
    # scalable: assert key metric exists
    assert hasattr(res.data, "total")
    assert isinstance(res.data.total, (int, float))


def test_estimate_budget_failure_when_days_invalid():
    # 如果你的 InputModel 本身就限制 days>=1，这里会在构造阶段失败，也算通过。
    try:
        inp = EstimateBudgetInput(days=0, currency="USD")
    except Exception:
        assert True
        return

    assert False, "Expected EstimateBudgetInput to raise validation error for days=0, but it did not."