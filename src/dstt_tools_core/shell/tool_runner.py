import os
from pathlib import Path
from typing import Dict, Any

from dstt_kernel.kernel import DsttKernal
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.resources.registry import ResourceRegistry
from dstt_tools_core.tools.reason.reason_spec import ReasonSpecRegistry
from dstt_tools_core.tools.reason.validators import ValidatorRegistry
from dstt_tools_core.tools.reason.reason_tools import register_reasoning_tools
from dstt_tools_core.tools.reason.capability_tools import register_capability_tools
from dstt_tools_core.tool_spec import ToolSpecRegistry
from dstt_tools_core.tool_specs import populate_default_spec_registry
from dstt_tools_core.resources.ollama import OllamaResource

DSTT_SCHEMA = """
DSTT JSON Structure:

{
  "segments": [
    {
      "transitions": [
        {
          "id": "string",
          "tool": "string",
          "inputs": ["string"],
          "outputs": ["string"]
        }
      ],
      "milestone": ["string"]
    }
  ]
}

Rules:

- segments is an ordered list
- transitions execute sequentially
- milestone defines outputs produced by the segment
- inputs must reference either initial inputs or previous milestone outputs
- final milestone must contain the final result
"""

class ToolRunner:
    """
    A minimal execution shell that bootstraps the full DSTT ecosystem natively.
    It acts entirely as an orchestrator bridging reasoning requests (via ReasonSpecs) 
    over to deterministic kernel execution boundaries.
    
    Reasoning Contract:
    The orchestrator is permitted to explicitly call `reason.run` outside the DSTT kernel 
    to bootstrap the initial plan, but all subsequent execution-bound reasoning MUST occur 
    through DSTT transitions.
    """
    def __init__(self, specs_directory: str = None):
        if not specs_directory:
            # Default lookup to internal `src/.../tools/reason/specs/`
            base_dir = Path(__file__).parent.parent
            specs_directory = str(base_dir / "tools" / "reason" / "specs")
            
        self._bootstrap_registries(specs_directory)
        self._kernel = DsttKernal()
        
    def _bootstrap_registries(self, specs_directory: str) -> None:
        """Initializes system boundaries logically insulating routing environments."""
        # 1. System capability definitions
        self.tool_spec_registry = ToolSpecRegistry()
        populate_default_spec_registry(self.tool_spec_registry)
        
        # 2. Execution bindings
        self.tool_registry = Registry()
        self.val_registry = ValidatorRegistry()
        
        self.resource_registry = ResourceRegistry()
        
        # Instantiate and bind local Ollama resource natively as the default system planner
        self.resource_registry.register("model.default_planner", OllamaResource(model_name="llama3.1:latest"))
        
        self.spec_registry = ReasonSpecRegistry()
        self.spec_registry.load_from_directory(specs_directory)
        
        # Note: Internal `ToolProvider` requires `ResourceRegistry` correctly configured.
        # This occurs safely downstream dynamically mapping mock models in the REPL or Tests.
        register_reasoning_tools(self.tool_registry, self.resource_registry, self.spec_registry, self.val_registry)
        
        runner_tool = self.tool_registry.get_tool("reason.run")
        register_capability_tools(self.tool_registry, runner_tool)
        
        from dstt_tools_core.tools.system.system import register_system_tools
        register_system_tools(self.tool_registry)
        
        from dstt_tools_core.tools.system.math import register_math_tools
        register_math_tools(self.tool_registry)
        
        self.provider = Provider(self.tool_registry)
        
        from dstt_tools_core.tools.bootstrap.bootstrap import register_bootstrap_tools
        register_bootstrap_tools(self.tool_registry, self.provider)
        
        from dstt_tools_core.tools.router_tools import register_router_tools
        register_router_tools(self.tool_registry, self.provider)
        
        from dstt_tools_core.tools.iterator_tools import register_iteration_tools
        register_iteration_tools(self.tool_registry, self.provider)
        
        # 3. Strategy Bindings dynamically instantiated as raw CompositeTools wrapping `reason.run` inside kernel scopes
        from dstt_tools_core.tool_specs.strategy_specs import STRATEGY_SPECS
        from dstt_tools_core.tools import CompositeTool
        
        for spec in STRATEGY_SPECS:
            self.tool_registry.register(spec["name"], CompositeTool(spec, self.provider))


    def run(self, task: str, input_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main execution loop. Translates human prompt -> Plan DAG -> DSTT Graph -> Execution State natively.
        Uses `strategySelect` to explicitly bootstrap the planning boundaries.
        """
        strategy_inputs = {
            "strategy_spec_id": "strategySelect",
            "task": task,
            "strategies": [
                "reason.plan.arithmetic",
                "reason.plan.general",
                "reason.plan.iteration"
            ],
            "key": "planner"
            
        }

            
        bootstrap_strategy_name = self.provider.lookup("bootstrap.strategy_select")


        
        # We must inject the explicit reasoning target id and its input context payload variables into the orchestration mapping natively
        
        
        planner_selected = self._kernel.execute(
            bootstrap_strategy_name,
            self.provider,
            initial_state=strategy_inputs
        )
        
        print("planner_selected =", planner_selected)
        print("planner_selected type =", type(planner_selected))

        planner_dstt_name = planner_selected.get("planner")
        print("planner_dstt_name =", planner_dstt_name)
        print("planner_dstt_name type =", type(planner_dstt_name))

        
        
        # When reasoning tools return a dynamically generated string or dict (such as Ollama) it might be wrapped in the 'execution_dstt' payload key natively due to the spec
        # Convert "reason.plan.arithmetic" -> "planArithmetic" to match the YAML file on disk perfectly
        if planner_dstt_name == "reason.plan.arithmetic":
            mapped_spec_id = "planArithmetic"
        elif planner_dstt_name == "reason.plan.general":
            mapped_spec_id = "planGeneral"
        else:
            mapped_spec_id = planner_dstt_name

        # Ensure required spec template variables are satisfied for planArithmetic.yaml correctly
        available_tools = [spec["name"] for spec in self.tool_spec_registry.get_all()]
        available_resources = self.resource_registry.list()
        
        planner_state = {
            "plan_spec_id": mapped_spec_id,
            "task": task,
            "tools": available_tools,
            "resources": available_resources,
            "dstt_schema": DSTT_SCHEMA
        }

        print("planner_state =", planner_state)
        print("planner_state type =", type(planner_state))

        bootstrap_planner = self.provider.lookup(planner_dstt_name)

        print("bootstrap_planner =", bootstrap_planner)
        print("bootstrap_planner type =", type(bootstrap_planner))

        execution_state = {
             "plan_spec_id": mapped_spec_id,
             "plan_inputs": planner_state
        }


        planner_output = self._kernel.execute(
            bootstrap_planner,
            self.provider,
            initial_state=execution_state
        )
        
        # The strategy spec deposits the generated graph into "execution_dstt"
        generated_dstt = planner_output.get("execution_dstt")
        if not generated_dstt:
            raise ValueError(f"Planner failed to generate 'execution_dstt'. State: {planner_output}")

        # Finally, execute the generated DSTT against the user's initial state
        final_state = self._kernel.execute(
            generated_dstt,
            self.provider,
            initial_state=input_state
        )

        return final_state
