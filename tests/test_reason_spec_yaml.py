import os
import pytest
from pathlib import Path
from dstt_tools_core.tools.reason.reason_spec import ReasonSpecRegistry

@pytest.fixture
def mock_yaml_directory(tmp_path):
    """Creates a temporary directory with a dummy ReasonSpec YAML file."""
    specs_dir = tmp_path / "specs"
    specs_dir.mkdir()
    
    mock_spec = specs_dir / "mock_plan.yaml"
    yaml_content = '''mode: plan
resource_domain: model
resource_id: model.qwen2.5
context:
  task: '{task}'
schema_target:
  type: array
determinism: strict
prompt_template: 'Solve {task}'
'''
    mock_spec.write_text(yaml_content)
    
    return str(specs_dir)

def test_load_yaml_from_directory(mock_yaml_directory):
    registry = ReasonSpecRegistry()
    registry.load_from_directory(mock_yaml_directory)
    
    # Assert the filename `mock_plan.yaml` was securely inherited as the spec_id
    spec = registry.get("mock_plan")
    
    assert spec["mode"] == "plan"
    assert spec["resource_domain"] == "model"
    assert spec["resource_id"] == "model.qwen2.5"
    assert spec["determinism"] == "strict"
    assert spec["prompt_template"] == "Solve {task}"
    assert spec["schema_target"]["type"] == "array"

def test_load_yaml_invalid_path():
    registry = ReasonSpecRegistry()
    with pytest.raises(ValueError, match="ReasonSpec directory not found"):
        registry.load_from_directory("/path/does/not/exist/ever")
        
    with pytest.raises(ValueError, match="ReasonSpec YAML file not found"):
        registry.load_from_file("/path/does/not/exist/file.yaml")
