import pytest
from dstt_tools_core.tools.reason.reason_spec import ReasonSpecRegistry, build_prompt
from dstt_tools_core.resources.registry import ResourceRegistry

# --- Mock Handlers ---

class MockEngine:
    def generate(self, prompt, schema=None):
        return "Repaired DSTT output"

# --- Fixtures ---

@pytest.fixture
def resource_registry():
    res_reg = ResourceRegistry()
    res_reg.register("model.qwen2.5", MockEngine())
    return res_reg

@pytest.fixture
def reason_spec_registry():
    registry = ReasonSpecRegistry()
    registry.register("repair_dstt", {
        "mode": "repair",
        "determinism": "strict",
        "resource_id": "model.qwen2.5",
        "prompt_template": "Target to Repair: {target}\\nError/Feedback: {error}\\nInstructions: Fix the DSTT structure."
    })
    return registry

# --- Tests ---

def test_reasonspec_blueprint_resolution(reason_spec_registry, resource_registry):
    # Verify exact user assertion block execution maps successfully against our abstractions
    spec = reason_spec_registry.get("repair_dstt")
    
    assert spec["mode"] == "repair"
    assert spec["determinism"] == "strict"
    
    # 1. Resource Registry fetches natively
    resource = resource_registry.get(spec["resource_id"])
    assert isinstance(resource, MockEngine)
    
    # 2. Builder resolves dictionary payloads purely from spec definition variables
    context = {
        "target": {"segments": []},
        "error": "missing milestone"
    }
    
    prompt = build_prompt("repair_dstt", spec, context)
    
    assert isinstance(prompt, str)
    assert "missing milestone" in prompt
    assert "Target to Repair: {'segments': []}" in prompt
    assert "Instructions: Fix the DSTT structure." in prompt

def test_missing_prompt_template():
    spec_ask = {"id": "my_ask_spec", "mode": "ask"}
    with pytest.raises(ValueError, match="ReasonSpec 'my_ask_spec' missing prompt_template"):
        build_prompt("my_ask_spec", spec_ask, {"prompt": "What is life?"})
        
    spec_unnamed = {"mode": "plan"}
    with pytest.raises(ValueError, match="ReasonSpec 'plan_spec' missing prompt_template"):
        build_prompt("plan_spec", spec_unnamed, {"task": "do thing"})
