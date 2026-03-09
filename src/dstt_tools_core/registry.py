from typing import Dict, List, Any
from .interfaces import UniversalTool

class Registry:
    """The catalog that holds the mapping of namespaces to tools."""
    
    def __init__(self):
        # { namespace: UniversalTool }
        self._store: Dict[str, UniversalTool] = {}
        
    def register(self, namespace: str, tool: UniversalTool) -> None:
        self._store[namespace] = tool
        
    def get_tool(self, namespace: str) -> UniversalTool:
        if namespace not in self._store:
            raise ValueError(f"Tool '{namespace}' not found.")
        return self._store[namespace]
        
    def list_namespaces(self) -> List[str]:
        return list(self._store.keys())
        
    def export_manifest(self) -> List[Dict[str, Any]]:
        manifest = []
        for namespace, tool in self._store.items():
            sig = tool.get_signature()
            manifest.append({
                "tool": namespace,
                "inputs": sig.get("inputs", []),
                "outputs": sig.get("outputs", [])
            })
        return manifest
