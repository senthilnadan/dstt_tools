import pytest
import urllib.request
from urllib.error import URLError

from dstt_tools_core.shell.tool_runner import ToolRunner
from dstt_tools_core.tools import NativeTool

def is_ollama_running() -> bool:
    """Checks if the local Ollama instance is actively running to prevent automated CI failures."""
    try:
        urllib.request.urlopen("http://localhost:11434/", timeout=1)
        return True
    except (URLError, Exception):
        return False

def mock_add(a: int, b: int) -> int: return a + b
def mock_sub(a: int, b: int) -> int: return a - b
def mock_mul(a: int, b: int) -> int: return a * b

@pytest.mark.skipif(not is_ollama_running(), reason="Local Ollama instance is not running")
def test_default_planner_integration():
    """
    Integration test asserting the dynamically bootstrapped `model.default_planner` (Ollama)
    can reason against mocked system tools securely natively.
    """
    runner = ToolRunner()
    
    # We allow the ToolRunner to use its natively bootstrapped `OllamaResource` 
    # for `model.default_planner`. We just rely on the real reasoning specs inside `dstt_tools_core/lib/reason/specs/`

    runner.tool_registry.register("math.add", NativeTool(mock_add))
    runner.tool_registry.register("math.subtract", NativeTool(mock_sub))
    runner.tool_registry.register("math.multiply", NativeTool(mock_mul))
    
    task = "Compute ((a + b) * (c - b))"
    initial_state = {"a": 2, "b": 5, "c": 3}
    
    result = runner.run(task, initial_state)
    
    # (2+5) * (3-5) = 7 * -2 = -14. The LLM might name the key `result`, `final_result`, etc.
    assert -14 in result.values(), f"Expected to find -14 in final state: {result}"
