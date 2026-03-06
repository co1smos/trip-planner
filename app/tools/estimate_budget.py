from app.models.tools import EstimateBudgetInput, EstimateBudgetOutput, ToolResult

def estimate_budget(input: EstimateBudgetInput) -> ToolResult:
    return ToolResult(
        ok=True,
        data=EstimateBudgetOutput(total=input.days * 100),  # dummy logic: $100 per day
        error=None,
        meta=None
    )