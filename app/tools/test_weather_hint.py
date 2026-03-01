import pytest

from app.models.tools import ToolResult, WeatherHintInput, WeatherHintOutput
from app.tools.weather_hint import weather_hint


@pytest.mark.anyio
async def test_weather_hint_ok_returns_typed_output():
    inp = WeatherHintInput(destination="tokyo")
    res = await weather_hint(inp)

    assert isinstance(res, ToolResult)
    assert isinstance(res.ok, bool)

    assert res.ok is True
    assert res.error is None
    assert isinstance(res.data, WeatherHintOutput)
    # scalable minimal assertion
    assert hasattr(res.data, "hint")
    assert isinstance(res.data.hint, str)