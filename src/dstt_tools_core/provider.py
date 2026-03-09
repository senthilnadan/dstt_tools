from typing import Any
from .registry import Registry

class Provider:
    """
    The bridge passed directly to the DSTT Kernel for executing tools.
    
    Reasoning Contract:
    ToolProviders must not introduce implicit reasoning behavior natively.
    """
    
    def __init__(self, registry: Registry):
        self._registry = registry
        
    def execute_transition(self, tool_path: str, *inputs) -> Any:
        tool = self._registry.get_tool(tool_path)
        return tool.execute(*inputs)

    def get(self, tool_path: str) -> Any:
        return self._registry.get_tool(tool_path)

    def lookup(self, tool_path: str) -> Any:
        print("tool_path =", tool_path)
        print("tool_path type =", type(tool_path))
        if not isinstance(tool_path, str):
            raise TypeError(f"Provider.lookup expected a string tool_path. Received {type(tool_path)} instead. Input payload:\n{tool_path}")
            
        tool = self._registry.get_tool(tool_path)
        if hasattr(tool, "_definition"):
            return tool._definition
        return tool
