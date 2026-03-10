from typing import Any, Dict, List, Optional
from dstt_tools_core.interfaces import UniversalTool
from dstt_tools_core.resources.registry import ResourceRegistry
from dstt_tools_core.tools.reason.reason_spec import ReasonSpecRegistry, build_prompt
from dstt_tools_core.tools.reason.validators import ValidatorRegistry, ReasonExecutionError

class ReasonRunTool(UniversalTool):
    """
    Executes reasoning deterministically utilizing a ReasonSpec definition.
    Binds the prompt configuration inherently to the execution lifecycle.
    """
    def __init__(self, resource_registry: ResourceRegistry, reason_spec_registry: ReasonSpecRegistry, validator_registry: Optional[ValidatorRegistry] = None):
        self._resource_registry = resource_registry
        self._spec_registry = reason_spec_registry
        self._validator_registry = validator_registry or ValidatorRegistry()

    def execute(self, spec_id: str, inputs: Dict[str, Any], attempt: int = 1, max_repair_attempts: int = 3) -> Any:
        if attempt > max_repair_attempts:
            raise ReasonExecutionError(f"Exceeded maximum repair limits ({max_repair_attempts}) for spec '{spec_id}'.")
            
        try:
            # Load declarative reasoning bounds
            print("spec_id =", spec_id)
            print("spec_id type =", type(spec_id))
            spec = self._spec_registry.get(spec_id)

        except ValueError as e:
            raise ReasonExecutionError(str(e))
        
        # Lookitively mandate external resources, explicit failure if unresolvable
        try:
            resource = self._resource_registry.get(spec["resource_id"])
        except Exception as e:
            # Re-wrap any missing resource definitions strictly
            if isinstance(e, KeyError) or "not found" in str(e).lower():
                raise ReasonExecutionError(f"Resource '{spec['resource_id']}' not found.")
            raise e
        
        # Build strict payload mapping against the inputs schema
        prompt = build_prompt(spec_id, spec, inputs)
        
        schema = spec.get("schema_target", None)
        
        if hasattr(resource, 'score'):
            return resource.score(prompt, inputs.get("candidates", []))
            
        elif hasattr(resource, 'generate'):
            if schema:
                result = resource.generate(prompt, schema=schema)
            else:
                result = resource.generate(prompt)
            
        elif schema:
            result = resource(prompt, schema=schema)
        else:
            result = resource(prompt)
            
        # Optional validation
        if "validator" in spec:
            try:
                validator = self._validator_registry.get(spec["validator"])
                validator.validate(result)
            except Exception as e:
                # If validation throws gracefully mapping against a strict boundary, repair.
                if spec.get("determinism", "relaxed") == "strict" and "repair_spec" in spec:
                    repair_inputs = {
                        "target": result, 
                        "error": str(e),
                        "original_spec": spec_id
                    }
                    # Recursive fallback bounded cleanly against limits
                    return self.execute(spec["repair_spec"], repair_inputs, attempt + 1, max_repair_attempts)
                elif isinstance(e, ReasonExecutionError):
                    # Validator lookup failures always bubble up explicitly
                    raise e
                else:
                    # Strict requirement fails outwardly if no repair map is declared
                    if spec.get("determinism", "relaxed") == "strict":
                        raise ReasonExecutionError(f"Strict validation failed without repair_spec: {e}")
                        
        return result

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["spec_id", "inputs"], "outputs": ["result"]}


class ReasonAskOracleTool(UniversalTool):
    """
    Direct access escape-hatch to a reasoning resource. 
    Bypasses ReasonSpec definitions strictly meant for debug/testing, NOT production pipes.
    """
    def __init__(self, resource_registry: ResourceRegistry):
        self._registry = resource_registry

    def execute(self, resource_id: str, prompt: str, schema: Optional[Any] = None) -> Any:
        resource = self._registry.get(resource_id)
        
        if hasattr(resource, 'generate'):
            if schema:
                 return resource.generate(prompt, schema=schema)
            return resource.generate(prompt)
            
        if schema:
            return resource(prompt, schema=schema)
        return resource(prompt)

    def get_signature(self) -> Dict[str, Any]:
        return {"inputs": ["resource_id", "prompt", "schema"], "outputs": ["response"]}


def register_reasoning_tools(
    registry, 
    resource_registry: ResourceRegistry, 
    reason_spec_registry: ReasonSpecRegistry, 
    validator_registry: Optional[ValidatorRegistry] = None,
    namespace_prefix: str = "reason"
):
    """Registers exclusively the primitive run orchestrator and debugging oracle capabilities."""
    registry.register(f"{namespace_prefix}.run", ReasonRunTool(resource_registry, reason_spec_registry, validator_registry))
    registry.register(f"{namespace_prefix}.ask_oracle", ReasonAskOracleTool(resource_registry))
