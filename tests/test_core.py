import pytest
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.tools import NativeTool
import system_lib

@pytest.fixture
def registry():
    reg = Registry()
    
    # Load system Library (math, system tools)
    mul_tool = NativeTool(system_lib.multiply)
    echo_tool = NativeTool(system_lib.echo)
    
    # Registering tools
    reg.register("math.multiply", mul_tool)
    reg.register("system.echo", echo_tool)
    return reg

@pytest.fixture
def provider(registry):
    return Provider(registry)

def test_tool_registration(registry):
    assert "math.multiply" in registry.list_namespaces()
    assert "system.echo" in registry.list_namespaces()
    
    # Check retrieval
    tool = registry.get_tool("math.multiply")
    assert isinstance(tool, NativeTool)

def test_manifest_export(registry):
    manifest = registry.export_manifest()
    
    # Asserting JSON structure matches spec
    assert len(manifest) == 2
    
    math_tool = next(item for item in manifest if item["tool"] == "math.multiply")
    assert math_tool["tool"] == "math.multiply"
    assert math_tool["inputs"] == ["a", "b"]
    assert math_tool["outputs"] == ["result"]
    
    system_tool = next(item for item in manifest if item["tool"] == "system.echo")
    assert system_tool["tool"] == "system.echo"
    assert system_tool["inputs"] == ["value"]
    assert system_tool["outputs"] == ["result"]

def test_non_existent_tool(provider):
    with pytest.raises(ValueError):
        provider.execute_transition("math.divide", 10, 5)

def test_invalid_path(provider):
    with pytest.raises(ValueError):
        provider.execute_transition("invalid_path", 10, 5)

def test_composite_tool_execution(registry, provider):
    from dstt_tools_core.tools import CompositeTool
    
    dstt_struct = {
        "inputs": ["x", "y", "z"],
        "outputs": ["final_result"],
        "segments": [
            {
                "transitions": [
                    {"id": "t1", "tool": "math.multiply", "inputs": ["x", "y"], "outputs": ["xy"]}
                ],
                "milestone": ["xy", "z"]
            },
            {
                "transitions": [
                    {"id": "t2", "tool": "math.multiply", "inputs": ["xy", "z"], "outputs": ["final_result"]}
                ],
                "milestone": ["final_result"]
            }
        ]
    }
    
    comp_tool = CompositeTool(dstt_struct, provider)
    registry.register("math.multiply_three", comp_tool)
    
    result = provider.execute_transition("math.multiply_three", 2, 3, 4)
    assert result == 24

def test_iterator_tools(registry, provider):
    from dstt_tools_core.lib.iterator_tools import register_iteration_tools
    register_iteration_tools(registry, provider)
    
    # Let's test `iterate` with square
    square_dstt = {
        "segments": [
            {
                "transitions": [
                    {"id": "t1", "tool": "math.multiply", "inputs": ["item", "item"], "outputs": ["square"]}
                ],
                "milestone": ["square"]
            }
        ]
    }
    
    # [1, 2, 3, 4] -> [1, 4, 9, 16]
    results = provider.execute_transition("iterators.iterate", [1, 2, 3, 4], square_dstt)
    assert results == [1, 4, 9, 16]

    # test iterate_reduce to sum a list
    def add(a, b): return a + b
    registry.register("math.add", NativeTool(add))
    
    sum_dstt = {
        "segments": [
            {
                "transitions": [
                    {"id": "t1", "tool": "math.add", "inputs": ["state", "item"], "outputs": ["state"]}
                ],
                "milestone": ["state"]
            }
        ]
    }
    
    # sum of [1,2,3,4] with initial state 0 -> 10
    total = provider.execute_transition("iterators.reduce", [1, 2, 3, 4], sum_dstt, 0)
    assert total == 10

def test_router_tools(registry, provider):
    from dstt_tools_core.lib.router_tools import register_router_tools
    register_router_tools(registry, provider)
    
    # 1. test switch_router
    res = provider.execute_transition("route.switch", "success", {"success": "dstt_A"})
    assert res == {"next_dstt": "dstt_A"}
    
    res = provider.execute_transition("route.switch", "fail", {"success": "dstt_A"})
    assert res == {"terminal_state": "fail"}
    
    # 2. test lookup_router
    res = provider.execute_transition("route.lookup", "A", {"A": "dstt_A"})
    assert res == {"next_dstt": "dstt_A"}

    # 3. test sequence_router
    res = provider.execute_transition("route.sequence", ["dstt_A", "dstt_B"], 1)
    assert res == {"next_dstt": "dstt_B"}
    res = provider.execute_transition("route.sequence", ["dstt_A", "dstt_B"], 5)
    assert res == {"terminal_state": "sequence_ended"}



