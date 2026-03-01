from app.models.tools import SearchPlacesInput, SearchPlacesOutput, ToolResult

async def search_places(input: SearchPlacesInput) -> ToolResult: 
    return ToolResult(
        ok=True,
        data=SearchPlacesOutput(result=f"Found places for query: {input.query}, the first place: Senso Ji temple"),
        error=None,
        meta=None
    )