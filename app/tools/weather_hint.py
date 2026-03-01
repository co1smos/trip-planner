from app.models.tools import WeatherHintInput, WeatherHintOutput, ToolResult

async def weather_hint(inp: WeatherHintInput) -> ToolResult:
    return ToolResult(
        ok=True,
        data=WeatherHintOutput(hint=f"The weather in {inp.destination} is sunny with a high of 25°C."),
        error=None,
        meta=None
    )   