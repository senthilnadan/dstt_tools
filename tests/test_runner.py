import pytest
from typing import Dict, Any

from dstt_tools_core.shell.tool_runner import ToolRunner
from dstt_tools_core.tools import NativeTool



def test_tool_runner_end_to_end_pipeline():
    """Validates the Shell Orchestrator triggers reasoning, parses DAG, and executes Kernel."""
    # Ensure reason specifications exist for the reasoning tools to map prompts properly.
    # The tests need raw strategy tools dynamically injected because ToolRunner no longer hardcodes them
    from dstt_tools_core.shell.tool_runner import ToolRunner
    runner = ToolRunner()
    
    test_cases = [
        # Original simple case
        ("Compute ((a + b) * (c - b))", {"a": 2, "b": 5, "c": 3}, -14),
        # Testing explicit order of operations directly
        #("Calculate the result of multiplying the sum of 12 and 8 by the difference between 30 and 15.", {}, 300),
        # Mixed sign computations and constant literal bindings
        #("Subtract 45 from 20, then multiply that result by negative 3.", {}, 75)
    ]

    for task, input_state, expected_result in test_cases:
        print(f"\n[TEST] Running Arithmetic Task: '{task}'")
        result = runner.run(task, input_state)
        
        # We assert that the final computed number appears SOMEWHERE inside the final state milestone evaluation dictionaries.
        # This prevents us from hardcoding checking against "result" vs "final_result" vs whatever the LLM arbitrarily named the variable.
        print(f"[TEST DEBUG] Actual output generated milestone dictionary:\n{result}\n")
        assert expected_result in result.values(), f"Expected mathematical target {expected_result} not found inside LLM output milestones: {result}"
