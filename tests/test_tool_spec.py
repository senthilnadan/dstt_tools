import pytest
from dstt_tools_core.tool_spec import ToolSpecRegistry

def test_tool_spec_register_and_get():
    registry = ToolSpecRegistry()
    spec = {
        "name": "math.add",
        "domain": "math",
        "description": "Adds two numbers",
        "inputs": [{"name": "a", "type": "number"}, {"name": "b", "type": "number"}],
        "outputs": [{"name": "sum", "type": "number"}],
        "determinism": "deterministic",
        "side_effects": False
    }
    registry.register(spec)
    
    retrieved = registry.get("math.add")
    assert retrieved == spec
    assert retrieved["domain"] == "math"

def test_tool_spec_list_by_domain():
    registry = ToolSpecRegistry()
    registry.register({"name": "math.add", "domain": "math"})
    registry.register({"name": "math.multiply", "domain": "math"})
    registry.register({"name": "web.search", "domain": "search"})
    
    math_tools = registry.list_by_domain("math")
    assert len(math_tools) == 2
    assert any(t["name"] == "math.add" for t in math_tools)
    
    search_tools = registry.list_by_domain("search")
    assert len(search_tools) == 1
    assert search_tools[0]["name"] == "web.search"

def test_tool_spec_invalid_lookup():
    registry = ToolSpecRegistry()
    with pytest.raises(ValueError, match="ToolSpec 'missing' not found."):
        registry.get("missing")

def test_tool_spec_missing_name():
    registry = ToolSpecRegistry()
    with pytest.raises(ValueError, match="ToolSpec must contain a 'name' field."):
        registry.register({"domain": "math"})
