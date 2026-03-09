import pytest
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.resources.registry import ResourceRegistry
from dstt_tools_core.lib.reason.reason_spec import ReasonSpecRegistry
from dstt_tools_core.lib.reason.validators import ValidatorRegistry, Validator, ReasonExecutionError
from dstt_tools_core.lib.reason.reason_tools import register_reasoning_tools

# --- Mock Ecosystem ---

class MockBrokenEngine:
    """Always generates a target missing the milestone requirement."""
    def generate(self, prompt: str, schema=None):
        return {"nodes": [{"id": "A"}], "status": "BROKEN DAG"}

class MockHealingEngine:
    """Specifically yields an output that passes validation."""
    def generate(self, prompt: str, schema=None):
        if "Instructions: Repair the milestone error" in prompt:
            return {"nodes": [{"id": "A", "milestone": True}], "status": "HEALED DAG"}
        return {"nodes": [{"id": "A"}], "status": "STILL BROKEN DAG"}

class MockDAGValidator(Validator):
    def validate(self, result):
        if "milestone" not in str(result):
            raise ValueError("Missing milestone")

# --- Fixtures ---

@pytest.fixture
def test_registries():
    res_reg = ResourceRegistry()
    res_reg.register("model.broken", MockBrokenEngine())
    res_reg.register("model.healer", MockHealingEngine())
    
    spec_reg = ReasonSpecRegistry()
    # Generates a broken DAG and validates it.
    spec_reg.register("plan_dag", {
        "mode": "plan",
        "determinism": "strict",
        "resource_id": "model.broken",
        "validator": "dag_validator",
        "repair_spec": "repair_dag",
        "prompt_template": "Task: {task}"
    })
    
    # Repairs targeting the broken DAG using healing engine
    spec_reg.register("repair_dag", {
        "mode": "repair",
        "determinism": "strict",
        "resource_id": "model.healer",
        "validator": "dag_validator",
        "prompt_template": "Target to Repair: {target}\\nError/Feedback: {error}\\nInstructions: Repair the milestone error"
    })
    
    # Never heals correctly to test execution limit
    spec_reg.register("plan_unrepairable", {
        "mode": "plan",
        "determinism": "strict",
        "resource_id": "model.broken",
        "validator": "dag_validator",
        "repair_spec": "repair_broken",
        "prompt_template": "Task: {task}"
    })
    
    spec_reg.register("repair_broken", {
        "mode": "repair",
        "determinism": "strict",
        "resource_id": "model.broken",
        "validator": "dag_validator",
        "repair_spec": "repair_broken",
        "prompt_template": "Error: {error}"
    })
    
    val_reg = ValidatorRegistry()
    val_reg.register("dag_validator", MockDAGValidator())
    
    return res_reg, spec_reg, val_reg
    
@pytest.fixture
def test_provider(test_registries):
    tool_registry = Registry()
    test_prov = Provider(tool_registry)
    register_reasoning_tools(tool_registry, *test_registries)
    return test_prov

# --- Tests ---

def test_successful_validation_and_repair(test_provider):
    """Verifies that an initial broken generation triggers a repair hitting model.healer and resolving cleanly."""
    res = test_provider.execute_transition("reason.run", "plan_dag", {"task": "test"})
    # It must evaluate strictly from the nested healer structure
    assert res["status"] == "HEALED DAG"

def test_fatal_repair_limits_exceeded(test_provider):
    """Ensures ReasonExecutionError is invoked statically protecting recursive iteration infinity."""
    with pytest.raises(ReasonExecutionError, match="Exceeded maximum repair limits"):
        test_provider.execute_transition("reason.run", "plan_unrepairable", {"task": "test"})

def test_missing_validator_raises_gracefully(test_provider, test_registries):
    """Checks the validator registry correctly denies execution paths requesting missing external evaluation rules."""
    res_reg, spec_reg, val_reg = test_registries
    spec_reg.register("missing_val", {
        "mode": "ask",
        "resource_id": "model.broken",
        "validator": "non_existent_validator",
        "prompt_template": "Test"
    })
    with pytest.raises(ReasonExecutionError, match="Validator 'non_existent_validator' not found in registry"):
        test_provider.execute_transition("reason.run", "missing_val", {"task": "test"})
