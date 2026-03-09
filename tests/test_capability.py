import pytest
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.resources.registry import ResourceRegistry
from dstt_tools_core.lib.reason.reason_spec import ReasonSpecRegistry
from dstt_tools_core.lib.reason.validators import ValidatorRegistry
from dstt_tools_core.lib.reason.reason_tools import register_reasoning_tools
from dstt_tools_core.lib.reason.capability_tools import register_capability_tools

class MockCapabilityEngine:
    """Simulates LLM evaluation over the tool constraints dynamically mapping the dictionaries."""
    def generate(self, prompt: str, schema=None):
        if "Find cheapest laptop" in prompt:
             return {
                 "filtered_tools": ["math.compare"],
                 "missing_capabilities": ["web.search"],
                 "satisfiable": False
             }
        
        # General math solving execution payload
        return {
            "filtered_tools": ["math.add", "math.multiply"],
            "missing_capabilities": [],
            "satisfiable": True
        }

@pytest.fixture
def test_setup():
    res_reg = ResourceRegistry()
    res_reg.register("model.router", MockCapabilityEngine())
    
    spec_reg = ReasonSpecRegistry()
    spec_reg.register("capability_resolution", {
        "mode": "ask_structured",
        "determinism": "strict",
        "resource_id": "model.router",
        "prompt_template": "Task: {task}\\nTools: {tool_inventory}",
        "schema_target": {
            "type": "object",
            "properties": {
                "filtered_tools": {"type": "array"},
                "missing_capabilities": {"type": "array"},
                "satisfiable": {"type": "boolean"}
            }
        }
    })
    
    val_reg = ValidatorRegistry()
    tool_registry = Registry()
    
    # Register internal reason orchestrator tools
    register_reasoning_tools(tool_registry, res_reg, spec_reg, val_reg)
    
    # Recover instantiated runner reference to bind properly into Capability rules natively
    runner = tool_registry.get_tool("reason.run")
    
    # Register integration tools bound into capabilities
    register_capability_tools(tool_registry, runner)
    
    return Provider(tool_registry)

def test_capability_resolve_satisfiable(test_setup):
    """Verifies typical mathematical pathing strips useless nodes mapping True satisfaction."""
    inputs = {
         "task": "Compute logic",
         "tool_inventory": ["math.add", "math.multiply", "web.search", "system.files"]
    }
    res = test_setup.execute_transition("capability.resolve", inputs["task"], inputs["tool_inventory"])
    
    assert res["satisfiable"] is True
    assert "web.search" not in res["filtered_tools"]
    assert "math.add" in res["filtered_tools"]
    assert len(res["missing_capabilities"]) == 0

def test_capability_resolve_unsatisfiable(test_setup):
    """Ensures complex tasks dynamically reject if constraints detect completely isolated capabilities required."""
    inputs = {
        "task": "Find cheapest laptop online",
        "tool_inventory": ["math.compare"]
    }
    res = test_setup.execute_transition("capability.resolve", inputs["task"], inputs["tool_inventory"])
    
    assert res["satisfiable"] is False
    assert "web.search" in res["missing_capabilities"]
    assert res["filtered_tools"] == ["math.compare"]
