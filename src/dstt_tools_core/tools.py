import inspect
from typing import Dict, Any, Callable
from .interfaces import UniversalTool

class NativeTool(UniversalTool):
    """
    Wraps standard Python functions. Auto-inspects arguments for its signature.
    
    Reasoning Contract:
    Tools must not invoke reasoning resources directly unless explicitly defined as `reason.*`.
    """
    
    def __init__(self, func: Callable):
        self._func = func
        
    def execute(self, *inputs) -> Any:
        return self._func(*inputs)
        
    def get_signature(self) -> Dict[str, Any]:
        sig = inspect.signature(self._func)
        inputs = list(sig.parameters.keys())
        # For simple native tools, we assume 'result' as the output to match spec
        return {
             "inputs": inputs,
             "outputs": ["result"]
        }

class CompositeTool(UniversalTool):
    """
    Wraps a DSTT JSON structure. Extracts its signature from the definition.
    
    Reasoning Contract:
    Tools must not invoke reasoning resources directly unless explicitly defined as `reason.*`.
    """
    
    def __init__(self, definition: Dict[str, Any], provider: Any = None):
        self._definition = definition
        self._provider = provider
        
    def _extract_dstt_signature(self) -> list:
        produced = set()
        signature = []
        segments = self._definition.get("segments", [])
        for segment in segments:
            for transition in segment.get("transitions", []):
                for inp in transition.get("inputs", []):
                    if inp not in produced and inp not in signature:
                        signature.append(inp)
                for out in transition.get("outputs", []):
                    produced.add(out)
        return signature

    def execute(self, *inputs) -> Any:
        if not self._provider:
            raise ValueError("Provider must be configured to execute CompositeTool.")
            
        from dstt_kernel.kernel import DsttKernal
        kernel = DsttKernal()
        
        sig = self._extract_dstt_signature()
        
        # Build initial state from positional inputs matching the defined input keys
        initial_state = dict(zip(sig, inputs))
        
        # Execute the nested DSTT graph
        result_state = kernel.execute(self._definition, self._provider, initial_state=initial_state)
        
        if len(result_state) == 1:
            return list(result_state.values())[0]
        else:
            return tuple(result_state.values())
        
    def get_signature(self) -> Dict[str, Any]:
        inputs = self._extract_dstt_signature()
        # Outputs can be determined from the final milestone
        segments = self._definition.get("segments", [])
        outputs = segments[-1].get("milestone", ["result"]) if segments else ["result"]
        
        return {
            "inputs": inputs,
            "outputs": outputs
        }
