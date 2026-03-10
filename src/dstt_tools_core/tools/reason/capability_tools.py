from typing import Any, Dict, List
from dstt_tools_core.interfaces import UniversalTool
from dstt_tools_core.tools.reason.reason_tools import ReasonRunTool

class CapabilityResolveTool(UniversalTool):
    """
    Evaluates an inventory of potential executing definitions strictly validating whether 
    a task is 'satisfiable', extracting a filtered list to guide Planner engines cleanly constraints.
    """
    def __init__(self, reason_run_tool: ReasonRunTool):
        self._runner = reason_run_tool

    def execute(self, task: str, tool_inventory: List[str]) -> Dict[str, Any]:
        """
        Executes capability filtering through the bound reasoning pipeline.
        
        Args:
            task: The user instruction to resolve.
            tool_inventory: Array of all theoretically available operation namespaces.
            
        Returns:
            Dict containing:
                - filtered_tools (list): Relevant items explicitly evaluated.
                - missing_capabilities (list): Tools not available needing procurement.
                - satisfiable (bool): Whether execution is statically possible right now.
        """
        inputs = {
            "task": task,
            "tool_inventory": tool_inventory
        }
        
        # Trigger explicit routing delegating complex extraction rules securely inside schemas
        return self._runner.execute("capability_resolution", inputs)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["task", "tool_inventory"], "outputs": ["filtered_tools", "missing_capabilities", "satisfiable"]}

def register_capability_tools(registry: Any, reason_run_tool: ReasonRunTool, namespace_prefix: str = "capability"):
    """
    Exposes the strictly defined orchestration steps formatting LLM outputs 
    to validate planning universes dynamically.
    """
    registry.register(f"{namespace_prefix}.resolve", CapabilityResolveTool(reason_run_tool))
