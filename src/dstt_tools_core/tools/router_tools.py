from typing import Any, Dict, List
from dstt_tools_core.interfaces import UniversalTool
from dstt_tools_core.tools import CompositeTool

def next(dstt: Any) -> Dict[str, Any]:
    return {"next_dstt": dstt}

def terminal(state: Any) -> Dict[str, Any]:
    return {"terminal_state": state}

class RouteByStateTool(UniversalTool):
    """Routes based on the value of a state variable."""
    def execute(self, state: str, routes: Dict[str, Any]) -> Dict[str, Any]:
        if state in routes:
            return next(routes[state])
        return terminal(state)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["state", "routes"], "outputs": ["result"]}

class RouteByPredicateTool(UniversalTool):
    """Routes based on evaluating predicates."""
    def __init__(self, provider: Any):
        self._provider = provider

    def execute(self, state: Any, predicates: List[Dict[str, Any]]) -> Dict[str, Any]:
        # predicates structure: [{"predicate": dstt, "dstt": dstt_target}]
        # or {"predicate": 'default', "dstt": dstt_target}
        for item in predicates:
            predicate_dstt = item.get("predicate")
            target_dstt = item.get("dstt")
            
            if predicate_dstt == "default":
                return next(target_dstt)
                
            comp_tool = CompositeTool(predicate_dstt, self._provider)
            sig_keys = comp_tool.get_signature()["inputs"]
            ctx = {"state": state}
            inputs = [ctx.get(k) for k in sig_keys]
            
            match = comp_tool.execute(*inputs)
            if match:
                return next(target_dstt)
                
        return terminal(state)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["state", "predicates"], "outputs": ["result"]}

class RouteByTableTool(UniversalTool):
    """Uses a routing table keyed by milestone state."""
    def execute(self, key: Any, routing_table: Dict[str, Any]) -> Dict[str, Any]:
        if key in routing_table:
            return next(routing_table[key])
        return terminal(key)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["key", "routing_table"], "outputs": ["result"]}

class RouteSequenceTool(UniversalTool):
    """Routes to the next DSTT in a predefined sequence."""
    def execute(self, sequence: List[Any], position: int) -> Dict[str, Any]:
        if 0 <= position < len(sequence):
            return next(sequence[position])
        return terminal("sequence_ended")

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["sequence", "position"], "outputs": ["result"]}

# --- Exploratory Routers (Placeholders for now) ---

class PlanNextTool(UniversalTool):
    """Uses reasoning to choose the next DSTT. (Placeholder)"""
    def execute(self, state: Any, candidate_dstts: List[Any]) -> Dict[str, Any]:
        if candidate_dstts:
            return next(candidate_dstts[0])
        return terminal(state)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["state", "candidate_dstts"], "outputs": ["result"]}

class RouteByScoreTool(UniversalTool):
    """Uses scoring functions to select the next path. (Placeholder)"""
    def execute(self, state: Any, candidates: List[Any], scoring_function: Any) -> Dict[str, Any]:
        if candidates:
            return next(candidates[0])
        return terminal(state)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["state", "candidates", "scoring_function"], "outputs": ["result"]}

class ExploreRoutesTool(UniversalTool):
    """Used in search-style systems. (Placeholder)"""
    def execute(self, state: Any, candidate_dstts: List[Any]) -> Dict[str, Any]:
        if candidate_dstts:
            return next(candidate_dstts[0])
        return terminal(state)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["state", "candidate_dstts"], "outputs": ["result"]}

def register_router_tools(registry, provider, namespace_prefix: str = "route"):
    """Convenience function to register all router tools."""
    registry.register(f"{namespace_prefix}.switch", RouteByStateTool())
    registry.register(f"{namespace_prefix}.predicate", RouteByPredicateTool(provider))
    registry.register(f"{namespace_prefix}.lookup", RouteByTableTool())
    registry.register(f"{namespace_prefix}.sequence", RouteSequenceTool())
    registry.register(f"{namespace_prefix}.plan", PlanNextTool())
    registry.register(f"{namespace_prefix}.score", RouteByScoreTool())
    registry.register(f"{namespace_prefix}.explore", ExploreRoutesTool())
