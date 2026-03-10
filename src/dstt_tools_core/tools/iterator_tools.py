from typing import Any, Dict, List
from dstt_tools_core.interfaces import UniversalTool
from dstt_tools_core.tools import CompositeTool

class IterateTool(UniversalTool):
    """Fundamental stateless iteration over a list of items."""
    def __init__(self, provider: Any):
        self._provider = provider
        
    def execute(self, items: List[Any], step_dstt: Dict[str, Any]) -> List[Any]:
        comp_tool = CompositeTool(step_dstt, self._provider)
        sig_keys = comp_tool.get_signature()["inputs"]
        
        results = []
        for item in items:
            ctx = {"item": item}
            inputs = [ctx.get(k) for k in sig_keys]
            res = comp_tool.execute(*inputs)
            results.append(res)
        return results

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["items", "step_dstt"], "outputs": ["results"]}

class IterateReduceTool(UniversalTool):
    """Stateful iteration with an accumulator."""
    def __init__(self, provider: Any):
        self._provider = provider
        
    def execute(self, items: List[Any], step_dstt: Dict[str, Any], initial_state: Any) -> Any:
        comp_tool = CompositeTool(step_dstt, self._provider)
        sig_keys = comp_tool.get_signature()["inputs"]
        
        state = initial_state
        for item in items:
            inp_state = {"state": state, "item": item}
            inputs = [inp_state.get(k) for k in sig_keys]
            state = comp_tool.execute(*inputs)
            
        return state

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["items", "step_dstt", "initial_state"], "outputs": ["final_state"]}

class IterateCollectTool(UniversalTool):
    """Conditional collection (filter-style iteration)."""
    def __init__(self, provider: Any):
        self._provider = provider
        
    def execute(self, items: List[Any], predicate_dstt: Dict[str, Any]) -> List[Any]:
        comp_tool = CompositeTool(predicate_dstt, self._provider)
        sig_keys = comp_tool.get_signature()["inputs"]
        
        results = []
        for item in items:
            ctx = {"item": item}
            inputs = [ctx.get(k) for k in sig_keys]
            keep = comp_tool.execute(*inputs)
            if keep:
                results.append(item)
        return results

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["items", "predicate_dstt"], "outputs": ["filtered_items"]}

class IterateFindTool(UniversalTool):
    """Search for the first matching element."""
    def __init__(self, provider: Any):
        self._provider = provider
        
    def execute(self, items: List[Any], predicate_dstt: Dict[str, Any]) -> Any:
        comp_tool = CompositeTool(predicate_dstt, self._provider)
        sig_keys = comp_tool.get_signature()["inputs"]
        
        for item in items:
            ctx = {"item": item}
            inputs = [ctx.get(k) for k in sig_keys]
            match = comp_tool.execute(*inputs)
            if match:
                return item
        return None

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["items", "predicate_dstt"], "outputs": ["item"]}

class IterateGroupTool(UniversalTool):
    """Group items by a computed key."""
    def __init__(self, provider: Any):
        self._provider = provider
        
    def execute(self, items: List[Any], key_dstt: Dict[str, Any]) -> Dict[Any, List[Any]]:
        comp_tool = CompositeTool(key_dstt, self._provider)
        sig_keys = comp_tool.get_signature()["inputs"]
        
        groups = {}
        for item in items:
            ctx = {"item": item}
            inputs = [ctx.get(k) for k in sig_keys]
            key = comp_tool.execute(*inputs)
            if key not in groups:
                groups[key] = []
            groups[key].append(item)
        return groups

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["items", "key_dstt"], "outputs": ["groups"]}

class IterateScanTool(UniversalTool):
    """Prefix accumulation that returns intermediate states."""
    def __init__(self, provider: Any):
        self._provider = provider
        
    def execute(self, items: List[Any], step_dstt: Dict[str, Any], initial_state: Any) -> List[Any]:
        comp_tool = CompositeTool(step_dstt, self._provider)
        sig_keys = comp_tool.get_signature()["inputs"]
        
        states = []
        state = initial_state
        for item in items:
            inp_state = {"state": state, "item": item}
            inputs = [inp_state.get(k) for k in sig_keys]
            state = comp_tool.execute(*inputs)
            states.append(state)
            
        return states

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["items", "step_dstt", "initial_state"], "outputs": ["states"]}

class IterateFlatMapTool(UniversalTool):
    """Each iteration step may return multiple outputs."""
    def __init__(self, provider: Any):
        self._provider = provider
        
    def execute(self, items: List[Any], step_dstt: Dict[str, Any]) -> List[Any]:
        comp_tool = CompositeTool(step_dstt, self._provider)
        sig_keys = comp_tool.get_signature()["inputs"]
        
        results = []
        for item in items:
            ctx = {"item": item}
            inputs = [ctx.get(k) for k in sig_keys]
            outputs = comp_tool.execute(*inputs)
            if not isinstance(outputs, (list, tuple)):
                outputs = [outputs]
            for output in outputs:
                results.append(output)
        return results

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["items", "step_dstt"], "outputs": ["flattened_results"]}

def register_iteration_tools(registry, provider, namespace_prefix: str = "iterators"):
    """Convenience function to register all iteration tools."""
    registry.register(f"{namespace_prefix}.iterate", IterateTool(provider))
    registry.register(f"{namespace_prefix}.reduce", IterateReduceTool(provider))
    registry.register(f"{namespace_prefix}.collect", IterateCollectTool(provider))
    registry.register(f"{namespace_prefix}.find", IterateFindTool(provider))
    registry.register(f"{namespace_prefix}.group", IterateGroupTool(provider))
    registry.register(f"{namespace_prefix}.scan", IterateScanTool(provider))
    registry.register(f"{namespace_prefix}.flatmap", IterateFlatMapTool(provider))
