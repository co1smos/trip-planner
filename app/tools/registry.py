from pydantic import BaseModel
from typing import Any, Callable

from app.models.tools import ToolResult, ToolError, SearchPlacesInput, SearchPlacesOutput, EstimateBudgetInput, EstimateBudgetOutput, WeatherHintInput, WeatherHintOutput
from app.tools.search_places import search_places
from app.tools.estimate_budget import estimate_budget
from app.tools.weather_hint import weather_hint

import anyio

class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, func: Callable[..., Any], input_model: type[BaseModel], output_model: type[BaseModel]):
        self.tools[name] = {
            "func": func,
            "input_model": input_model,
            "output_model": output_model,
        }

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())

    def get_input_model(self, tool_name: str) -> type[BaseModel]:
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        return tool["input_model"]

    def get_output_model(self, tool_name: str) -> type[BaseModel]:
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        return tool["output_model"]

    async def call(self, tool_name: str, args: dict, *, timeout_s: float | None = None) -> ToolResult:
        tool_func = self.tools.get(tool_name)
        if not tool_func:
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    type="NOT_FOUND",
                    message=f"Tool not found: {tool_name}",
                    retryable=False,
                    details=None
                ),
                meta=None,
            )
        
        try:
            input_model = self.get_input_model(tool_name)
            input = input_model.model_validate(args)
        except Exception as e:
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    type="VALIDATION_ERROR",
                    message=f"Invalid input for tool {tool_name}: {str(e)}",
                    retryable=False,
                    details=None
                ),
                meta=None,
            )

        try:
            if timeout_s is not None:
                with anyio.fail_after(timeout_s) as scope:
                    result = await tool_func["func"](input)
                # result = await asyncio.wait_for(tool_func["func"](input), timeout=timeout_s) both works
            else:
                result = await tool_func["func"](input)
        except Exception as e:
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    type="TOOL_EXCEPTION",
                    message=f"Exception when calling tool {tool_name}: {type(e)} : {str(e)}",
                    retryable=False,
                    details=None
                ),
                meta=None,
            )
        
        try:
            output_model = self.get_output_model(tool_name)
            output = output_model.model_validate(result.data)
            return ToolResult(
                ok=True,
                data=output,
                error=None,
                meta=None,
            )
        except Exception as e:
            return ToolResult(
                ok=False,
                data=None,
                error=ToolError(
                    type="VALIDATION_ERROR",
                    message=f"Invalid output for tool {tool_name}: {str(e)}",
                    retryable=False,
                    details=None
                ),
                meta=None,
            )


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(
        name="search_places",
        func=search_places,
        input_model=SearchPlacesInput,
        output_model=SearchPlacesOutput, 
    )
    registry.register(
        name="estimate_budget",
        func=estimate_budget,
        input_model=EstimateBudgetInput,
        output_model=EstimateBudgetOutput, 
    )
    registry.register(
        name="weather_hint",
        func=weather_hint,
        input_model=WeatherHintInput,
        output_model=WeatherHintOutput, 
    )
    return registry
