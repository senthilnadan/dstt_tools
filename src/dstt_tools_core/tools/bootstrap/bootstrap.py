from typing import Any, Dict
from dstt_tools_core.interfaces import UniversalTool
from dstt_tools_core.tools import CompositeTool, NativeTool
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider

def build_strategy_inputs(task: str) -> Dict[str, Any]:
    return {
        "task": task,
        "strategies": [
            "reason.plan.arithmetic",
            "reason.plan.general",
            "reason.plan.iteration"
        ],
        "key": "planner"
    }

# Barebones DSTT implementing simply Strategy Selection against `reason.run` inside a single execution block natively.
strategy_select_dstt = {
    "segments": [{
        "transitions": [
            {
                "id": "t0",
                "tool": "bootstrap.build_strategy_inputs",
                "inputs": ["task"],
                "outputs": ["strategy_inputs"]
            },
            {
                "id": "t1",
                "tool": "reason.run",
                "inputs": ["strategy_spec_id", "strategy_inputs"],
                "outputs": ["reasoning_output"]
            },
            {
                "id": "t2",
                "tool": "system.get_value",
                "inputs": ["reasoning_output", "key"],
                "outputs": ["planner"]
            }

        ],
        "milestone": ["planner"]
    }]
}

plan_arithmetic_dstt = {
    "segments": [{
        "transitions": [
            {
                "id": "t0",
                "tool": "bootstrap.build_strategy_inputs",
                "inputs": ["task"],
                "outputs": ["strategy_inputs"]
            },
            {
                "id": "t1",
                "tool": "reason.run",
                "inputs": ["strategy_spec_id", "strategy_inputs"],
                "outputs": ["reasoning_output"]
            },
            {
                "id": "t2",
                "tool": "system.get_value",
                "inputs": ["reasoning_output", "key"],
                "outputs": ["planner"]
            }

        ],
        "milestone": ["planner"]
    }]
}


def register_bootstrap_tools(registry: Registry, provider: Provider, namespace_prefix: str = "bootstrap"):
    """
    Registers minimal orchestration strategies to securely map human input into the reasoning planning namespace.
    """
    registry.register(
        f"{namespace_prefix}.build_strategy_inputs",
        NativeTool(build_strategy_inputs)
    )
    registry.register(
        f"{namespace_prefix}.strategy_select", 
        CompositeTool(strategy_select_dstt, provider)
    )
    registry.register(
        f"reason.plan.arithmetic", 
        CompositeTool(plan_arithmetic_dstt, provider)
    )
    
    
