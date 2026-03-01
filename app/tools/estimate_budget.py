from app.models.tools import EstimateBudgetInput, EstimateBudgetOutput, ToolResult

def estimate_budget(input: EstimateBudgetInput) -> ToolResult:
    return ToolResult(
        ok=True,
        data=EstimateBudgetOutput(total=100),
        error=None,
        meta=None
    )