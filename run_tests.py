import sys
from pathlib import Path

base_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(base_dir / "src"))
sys.path.insert(0, str(base_dir.parent / "dstt" / "src"))

from tests.test_runner import test_tool_runner_end_to_end_pipeline
from tests.test_default_planner import test_default_planner_integration

print("test_runner: START")
try:
    test_tool_runner_end_to_end_pipeline()
    print("test_runner: SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()

"""
print("test_default_planner: START")
try:
    test_default_planner_integration()
    print("test_default_planner: SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
"""