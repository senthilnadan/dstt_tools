from typing import Any, Dict
from dstt_tools_core.interfaces import UniversalTool

class StateGetTool(UniversalTool):
    """
    Evaluates maps dynamically bypassing literal Python dict extractions across orchestrators.
    """
    def execute(self, obj: Dict[str, Any], key: str) -> Any:
        if not isinstance(obj, dict):
            return obj
        if key not in obj:
            raise KeyError(f"Key '{key}' not found in object")
        return obj[key]        

    def get_signature(self) -> Dict[str, Any]:
        return {
            "inputs": ["obj", "key"],
            "outputs": ["value"]
        }

class GetValueTool(UniversalTool):
    """
    Recursively extracts the first string value found in a nested structure.
    Useful for unboxing non-deterministic LLM JSON outputs.
    """
    def execute(self, obj: Any, key: str) -> Any:
        if isinstance(obj, dict):
            return obj[key]
        else:
            raise TypeError("obj must be a dict")

    def get_signature(self) -> Dict[str, Any]:
        return {
            "inputs": ["obj"],
            "outputs": ["value"]
        }

def register_system_tools(registry: Any, namespace_prefix: str = "system"):
    """
    Exposes minimal capability mappings natively.
    """
    registry.register(f"{namespace_prefix}.get", StateGetTool())
    registry.register(f"{namespace_prefix}.get_value", GetValueTool())
