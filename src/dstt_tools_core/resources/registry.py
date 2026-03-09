from typing import Any, List, Dict

class ResourceRegistry:
    """
    Provides a stable mechanism to register, discover, and retrieve external execution resources.
    Resources represent execution engines such as language models, solvers, search systems, APIs.
    """
    
    def __init__(self):
        # Maps namespace identifier (e.g. "model.qwen2.5") to the concrete resource instance
        self._resources: Dict[str, Any] = {}

    def register(self, name: str, resource: Any) -> None:
        """Register a resource with the system under a namespaced id (e.g. domain.name)."""
        self._resources[name] = resource

    def get(self, name: str) -> Any:
        """Retrieve a resource by its exact identifier."""
        if name not in self._resources:
            raise ValueError(f"Resource '{name}' not found.")
        return self._resources[name]

    def list(self) -> List[str]:
        """List all globally registered resource names."""
        return list(self._resources.keys())

    def list_by_domain(self, domain: str) -> List[str]:
        """List resources belonging to a specific domain (e.g. 'model')."""
        prefix = f"{domain}."
        return [name for name in self._resources.keys() if name.startswith(prefix)]
