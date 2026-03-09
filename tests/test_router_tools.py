import pytest
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.tools import NativeTool
from dstt_tools_core.lib.router_tools import register_router_tools

# --- Native Math Helpers ---
def is_even(val): return val % 2 == 0
def is_positive(val): return val > 0

# --- Fixtures ---
@pytest.fixture
def registry():
    reg = Registry()
    reg.register("math.is_even", NativeTool(is_even))
    reg.register("math.is_positive", NativeTool(is_positive))
    return reg

@pytest.fixture
def provider(registry):
    prov = Provider(registry)
    register_router_tools(registry, prov)
    return prov


# --- Tests ---

def test_switch_router(provider):
    routes = {
        "success": "dstt_A",
        "retry": "dstt_B"
    }
    
    # State matches -> Return target DSTT
    res1 = provider.execute_transition("route.switch", "success", routes)
    assert res1 == {"next_dstt": "dstt_A"}
    
    # State doesn't match -> Terminal state
    res2 = provider.execute_transition("route.switch", "fail", routes)
    assert res2 == {"terminal_state": "fail"}


def test_lookup_router(provider):
    routing_table = {
        "A": "dstt_A",
        "B": "dstt_B"
    }
    
    # Key matches -> Return target DSTT
    res1 = provider.execute_transition("route.lookup", "A", routing_table)
    assert res1 == {"next_dstt": "dstt_A"}
    
    # Key doesn't match -> Terminal state
    res2 = provider.execute_transition("route.lookup", "C", routing_table)
    assert res2 == {"terminal_state": "C"}


def test_sequence_router(provider):
    seq = ["dstt_A", "dstt_B", "dstt_C"]
    
    # Within bounds
    res1 = provider.execute_transition("route.sequence", seq, 0)
    assert res1 == {"next_dstt": "dstt_A"}
    res2 = provider.execute_transition("route.sequence", seq, 2)
    assert res2 == {"next_dstt": "dstt_C"}
    
    # Out of bounds
    res3 = provider.execute_transition("route.sequence", seq, 3)
    assert res3 == {"terminal_state": "sequence_ended"}
    res4 = provider.execute_transition("route.sequence", seq, -1)
    assert res4 == {"terminal_state": "sequence_ended"}


def test_predicate_router(provider):
    is_positive_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.is_positive", "inputs": ["state"], "outputs": ["match"]}],
            "milestone": ["match"]
        }]
    }
    
    is_even_dstt = {
        "segments": [{
            "transitions": [{"id": "t1", "tool": "math.is_even", "inputs": ["state"], "outputs": ["match"]}],
            "milestone": ["match"]
        }]
    }
    
    predicates = [
        {"predicate": is_positive_dstt, "dstt": "dstt_positive"},
        {"predicate": is_even_dstt, "dstt": "dstt_even"},
        {"predicate": "default", "dstt": "dstt_fallback"}
    ]
    
    # 10 is positive -> match first predicate
    res1 = provider.execute_transition("route.predicate", 10, predicates)
    assert res1 == {"next_dstt": "dstt_positive"}
    
    # -2 is not positive, but is even -> match second predicate
    res2 = provider.execute_transition("route.predicate", -2, predicates)
    assert res2 == {"next_dstt": "dstt_even"}
    
    # -3 is neither -> match default
    res3 = provider.execute_transition("route.predicate", -3, predicates)
    assert res3 == {"next_dstt": "dstt_fallback"}
    
    # What if no default and no match?
    strict_predicates = [
        {"predicate": is_positive_dstt, "dstt": "dstt_positive"}
    ]
    res4 = provider.execute_transition("route.predicate", -5, strict_predicates)
    assert res4 == {"terminal_state": -5}


# --- Placeholder Tests ---

def test_plan_next(provider):
    candidates = ["dstt_A", "dstt_B"]
    res1 = provider.execute_transition("route.plan", "state", candidates)
    assert res1 == {"next_dstt": "dstt_A"}  # placeholder returns first
    
    res2 = provider.execute_transition("route.plan", "state", [])
    assert res2 == {"terminal_state": "state"}


def test_route_by_score(provider):
    candidates = ["dstt_1", "dstt_2"]
    def dummy_score(x): return 1
    
    res1 = provider.execute_transition("route.score", "state", candidates, dummy_score)
    assert res1 == {"next_dstt": "dstt_1"} # placeholder returns first
    
    res2 = provider.execute_transition("route.score", "state", [], dummy_score)
    assert res2 == {"terminal_state": "state"}


def test_explore_routes(provider):
    candidates = ["dstt_x", "dstt_y"]
    res1 = provider.execute_transition("route.explore", "state", candidates)
    assert res1 == {"next_dstt": "dstt_x"} # placeholder returns first
    
    res2 = provider.execute_transition("route.explore", "state", [])
    assert res2 == {"terminal_state": "state"}
