from typing import Any, Dict

class ReasonExecutionError(Exception):
    """Raised when the Reason Runtime encounters unresolvable errors or exceeds repair limits."""
    pass

class ValidationError(Exception):
    """Structured exception containing specific feedback formatting evaluated during repair scopes."""
    def __init__(self, error_type: str, location: str, message: str):
        self.error_type = error_type
        self.location = location
        self.message = message
        self.details_dict = {"error_type": error_type, "location": location, "message": message}
        super().__init__(f"{error_type} at {location}: {message}")

class Validator:
    """Core interface for all ReasonSpec structural validators."""
    def validate(self, result: Any) -> None:
        """Enforce validation rules against the result. Should raise ValueError or AssertionError on mismatch."""
        raise NotImplementedError

class ValidatorRegistry:
    """Maintains external validators referenced by ReasonSpecs."""
    def __init__(self):
        self._validators: Dict[str, Validator] = {}

    def register(self, name: str, validator: Validator) -> None:
        self._validators[name] = validator

    def get(self, name: str) -> Validator:
        if name not in self._validators:
            raise ReasonExecutionError(f"Validator '{name}' not found in registry.")
        return self._validators[name]

# --- Concrete Implementations ---

class SchemaValidator(Validator):
    """Validates that a generated dictionary precisely contains the strict expected fields mapped from configuration."""
    def __init__(self, required_keys: list[str]):
        self.required_keys = required_keys

    def validate(self, result: Any) -> None:
        if not isinstance(result, dict):
            raise ValidationError("schema_mismatch", "root", "Result must be a dictionary object.")
            
        for key in self.required_keys:
            if key not in result:
                raise ValidationError("missing_field", f"root.{key}", f"Required field '{key}' is missing from the output schema.")

class DagValidator(Validator):
    """Ensures deterministic structures without topological cycles or duplicate evaluation strings."""
    def validate(self, result: Any) -> None:
        if not isinstance(result, dict) or "nodes" not in result:
             raise ValidationError("invalid_structure", "root", "DAG requires a 'nodes' array.")
             
        nodes = result["nodes"]
        if not isinstance(nodes, list):
             raise ValidationError("invalid_structure", "root.nodes", "Nodes must be a list of configuration objects.")
             
        seen_ids = set()
        for i, node in enumerate(nodes):
            node_id = node.get("id")
            if not node_id:
                raise ValidationError("missing_id", f"nodes[{i}]", "Node lacks a unique identifier.")
            if node_id in seen_ids:
                raise ValidationError("duplicate_id", f"nodes[{i}]", f"Node identifier '{node_id}' is not unique.")
            seen_ids.add(node_id)
            
        # Optional cyclic check
        for i, node in enumerate(nodes):
             for dep in node.get("dependencies", []):
                 if dep not in seen_ids:
                      raise ValidationError("invalid_dependency", f"nodes[{i}]", f"Dependency '{dep}' does not exist.")


class DsttValidator(Validator):
    """Validates fundamental structural transitions across simulated DSTT evaluations."""
    def validate(self, result: Any) -> None:
        if not isinstance(result, dict) or "segments" not in result:
            raise ValidationError("invalid_structure", "root", "DSTT evaluation requires 'segments' definitions.")
            
        segments = result["segments"]
        for i, segment in enumerate(segments):
            if "outputs" not in segment or not isinstance(segment.get("outputs"), list):
                raise ValidationError("missing_outputs", f"segments[{i}]", "Segment must declare explicit outputs.")
            if segment.get("is_milestone") and not segment["outputs"]:
                 raise ValidationError("milestone_discipline", f"segments[{i}]", "Milestone segments must declare outputs.")
