import pytest
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.resources.registry import ResourceRegistry
from dstt_tools_core.lib.reason.reason_spec import ReasonSpecRegistry
from dstt_tools_core.lib.reason.reason_tools import register_reasoning_tools

# --- Mock Resource Engine ---

class MockReasoningEngine:
    def generate(self, prompt: str, schema=None):
        if schema:
             return {"mock_structured_response": prompt, "enforced_schema": schema}
             
        # Mock payload check to dynamically distinguish prompt execution behavior bounds
        if "Missing milestone" in prompt:
            return "Repaired target successfully"
            
        return f"Mocked response for: {prompt}"

# --- Fixtures ---

@pytest.fixture
def resource_registry():
    res_reg = ResourceRegistry()
    res_reg.register("model.qwen", MockReasoningEngine())
    return res_reg

@pytest.fixture
def spec_registry():
    sr = ReasonSpecRegistry()
    sr.register("plan_dag", {
        "mode": "plan",
        "determinism": "strict",
        "resource_id": "model.qwen",
        "schema_target": {"type": "object", "properties": {"nodes": {"type": "array"}}},
        "prompt_template": "Task: {task}\\nAvailable Tools: {tools}"
    })
    
    sr.register("repair_dstt", {
        "mode": "repair",
        "determinism": "strict",
        "resource_id": "model.qwen",
        "prompt_template": "Target to Repair: {target}\\nError/Feedback: {error}"
    })
    return sr

@pytest.fixture
def tool_registry():
    return Registry()

@pytest.fixture
def test_provider(tool_registry, resource_registry, spec_registry): 
    test_prov = Provider(tool_registry)
    register_reasoning_tools(tool_registry, resource_registry, spec_registry)
    return test_prov

# --- Tests ---

def test_reason_run_plan(test_provider):
    """Ensure ReasonRunTool parses the structured request and forwards schema to Resource appropriately."""
    inputs = {
        "task": "Compute trajectory",
        "tools": ["system.calc"]
    }
    
    res = test_provider.execute_transition("reason.run", "plan_dag", inputs)
    
    # Check strict format propagation locally
    assert "Task: Compute trajectory" in res["mock_structured_response"]
    assert "Available Tools: ['system.calc']" in res["mock_structured_response"]
    assert "nodes" in res["enforced_schema"]["properties"]

def test_reason_run_repair(test_provider):
    """Ensure ReasonRunTool builds heuristic string arrays without schema constraints cleanly against target dicts."""
    inputs = {
        "target": "BROKEN DAG",
        "error": "Missing milestone requirement."
    }
    
    res = test_provider.execute_transition("reason.run", "repair_dstt", inputs)
    
    # Assert specific mock execution trigger returns generic parsed repair string
    assert res == "Repaired target successfully"

def test_ask_oracle_override(test_provider):
    """Test debugging escape-hatch that natively hits ResourceRegistry ignoring ReasonSpecs."""
    res = test_provider.execute_transition("reason.ask_oracle", "model.qwen", "Raw diagnostic check")
    
    assert res == "Mocked response for: Raw diagnostic check"
    
    structured_res = test_provider.execute_transition(
        "reason.ask_oracle", "model.qwen", "Check", {"type": "string"}
    )
    assert structured_res["enforced_schema"] == {"type": "string"}
    assert structured_res["mock_structured_response"] == "Check"
