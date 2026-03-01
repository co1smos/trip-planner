import pytest

from app.models.tools import ToolResult, SearchPlacesInput, SearchPlacesOutput
from app.tools.search_places import search_places


@pytest.mark.anyio
async def test_search_places_ok_returns_typed_output():
    inp = SearchPlacesInput(query="tokyo")
    res = await search_places(inp)

    assert isinstance(res, ToolResult)
    assert res.ok is True

    assert res.error is None
    assert isinstance(res.data, SearchPlacesOutput)
    # scalable minimal assertions: output model exists + core field type
    assert hasattr(res.data, "result")
    assert isinstance(res.data.result, str)


@pytest.mark.anyio
async def test_search_places_failure_shape_if_you_choose_to_fail_on_empty_query():
    # 如果你的 SearchPlacesInput 允许空 query，这个测试会失败。
    # 推荐：Input 模型用 min_length=1，这样 validation 在 registry 层或模型层完成。
    # 这里我们只做“可选失败用例”：如果构造失败，说明模型做了校验（也算通过）。
    try:
        inp = SearchPlacesInput(query="")
    except Exception:
        assert True
        return
    
    assert False, "Expected SearchPlacesInput to raise validation error for empty query, but it did not."