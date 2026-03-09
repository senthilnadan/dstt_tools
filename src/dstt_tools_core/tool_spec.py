from typing import Dict, Any, List

class ToolSpecRegistry:
    """
    Registry for storing descriptive ToolSpec definitions for discovery.
    This acts purely as metadata allowing planners to logically reason about interfaces.
    """
    
    def __init__(self):
        self._specs: Dict[str, Dict[str, Any]] = {}
        
    def register(self, spec: Dict[str, Any]) -> None:
        """Registers a descriptive ToolSpec into the routing registry."""
        name = spec.get("name")
        if not name:
            raise ValueError("ToolSpec must contain a 'name' field.")
        self._specs[name] = spec
        
    def get(self, name: str) -> Dict[str, Any]:
        """Retrieves a specific ToolSpec by its exact namespace mapping."""
        if name not in self._specs:
            raise ValueError(f"ToolSpec '{name}' not found.")
        return self._specs[name]
        
    def list_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Returns all tools belonging to a distinct capability domain (e.g. 'math')."""
        return [spec for spec in self._specs.values() if spec.get("domain") == domain]
        
    def get_all(self) -> List[Dict[str, Any]]:
        """Returns the full universe of registered ToolSpecs."""
        return list(self._specs.values())
