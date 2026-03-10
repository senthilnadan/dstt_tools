import pytest
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.tools import NativeTool
from dstt_tools_core.tools.iterator_tools import register_iteration_tools

# --- Native Math Helpers ---
def multiply(a, b): return a * b
def add(a, b): return a + b
def is_even(val): return val % 2 == 0
def group_parity(val): return "even" if val % 2 == 0 else "odd"
def get_adjacent(val): return [val - 1, val + 1]

# --- Fixtures ---
@pytest.fixture
def registry():
    reg = Registry()
    reg.register("math.multiply", NativeTool(multiply))
    reg.register("math.add", NativeTool(add))
    reg.register("math.is_even", NativeTool(is_even))
    reg.register("math.group_parity", NativeTool(group_parity))
    reg.register("math.get_adjacent", NativeTool(get_adjacent))
    return reg

@pytest.fixture
def provider(registry):
    prov = Provider(registry)
    register_iteration_tools(registry, prov)
    return prov


# --- Tests ---

def test_iterate(provider):
    square_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.multiply", "inputs": ["item", "item"], "outputs": ["square"]}],
            "milestone": ["square"]
        }]
    }
    # [1, 2, 3] -> [1, 4, 9]
    res = provider.execute_transition("iterators.iterate", [1, 2, 3], square_dstt)
    assert res == [1, 4, 9]

def test_iterate_reduce(provider):
    sum_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.add", "inputs": ["state", "item"], "outputs": ["state"]}],
            "milestone": ["state"]
        }]
    }
    # sum of [1, 2, 3, 4] with initial_state=0 -> 10
    total = provider.execute_transition("iterators.reduce", [1, 2, 3, 4], sum_dstt, 0)
    assert total == 10

def test_iterate_collect(provider):
    even_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.is_even", "inputs": ["item"], "outputs": ["keep"]}],
            "milestone": ["keep"]
        }]
    }
    # Filter evens from [1, 2, 3, 4] -> [2, 4]
    evens = provider.execute_transition("iterators.collect", [1, 2, 3, 4], even_dstt)
    assert evens == [2, 4]

def test_iterate_find(provider):
    even_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.is_even", "inputs": ["item"], "outputs": ["match"]}],
            "milestone": ["match"]
        }]
    }
    # Find first even in [1, 3, 4, 5] -> 4
    match = provider.execute_transition("iterators.find", [1, 3, 4, 5], even_dstt)
    assert match == 4
    # Find first even in [1, 3, 5] -> None
    none_match = provider.execute_transition("iterators.find", [1, 3, 5], even_dstt)
    assert none_match is None

def test_iterate_group(provider):
    parity_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.group_parity", "inputs": ["item"], "outputs": ["key"]}],
            "milestone": ["key"]
        }]
    }
    # Group [1, 2, 3, 4] -> {"odd": [1, 3], "even": [2, 4]}
    groups = provider.execute_transition("iterators.group", [1, 2, 3, 4], parity_dstt)
    assert groups == {"odd": [1, 3], "even": [2, 4]}

def test_iterate_scan(provider):
    sum_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.add", "inputs": ["state", "item"], "outputs": ["state"]}],
            "milestone": ["state"]
        }]
    }
    # scan of [1, 2, 3] with initial_state=0 -> [1, 3, 6]
    scans = provider.execute_transition("iterators.scan", [1, 2, 3], sum_dstt, 0)
    assert scans == [1, 3, 6]

def test_iterate_flatmap(provider):
    adj_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.get_adjacent", "inputs": ["item"], "outputs": ["adj"]}],
            "milestone": ["adj"]
        }]
    }
    # flatmap [2, 5] -> [1, 3, 4, 6]
    flat = provider.execute_transition("iterators.flatmap", [2, 5], adj_dstt)
    assert flat == [1, 3, 4, 6]
