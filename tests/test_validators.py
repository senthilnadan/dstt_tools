import pytest
from dstt_tools_core.tools.reason.validators import (
    SchemaValidator, 
    DagValidator, 
    DsttValidator, 
    ValidationError
)

def test_schema_validator():
    val = SchemaValidator(["plan_name", "confidence"])
    
    # Success
    val.validate({"plan_name": "A", "confidence": 0.9})
    
    # Failure map
    with pytest.raises(ValidationError) as exc:
        val.validate({"plan_name": "A"})
    
    assert exc.value.error_type == "missing_field"
    assert exc.value.location == "root.confidence"
    
def test_dag_validator():
    val = DagValidator()
    
    # Success
    val.validate({
        "nodes": [
            {"id": "A", "dependencies": []},
            {"id": "B", "dependencies": ["A"]}
        ]
    })
    
    # Missing nodes list
    with pytest.raises(ValidationError) as exc1:
        val.validate({})
    assert exc1.value.error_type == "invalid_structure"
    
    # Duplicate identifier
    with pytest.raises(ValidationError) as exc2:
        val.validate({
            "nodes": [
                {"id": "A"},
                {"id": "A"}
            ]
        })
    assert exc2.value.error_type == "duplicate_id"
    
    # Invalid dependency resolution
    with pytest.raises(ValidationError) as exc3:
        val.validate({
            "nodes": [
                {"id": "A", "dependencies": ["C"]}
            ]
        })
    assert exc3.value.error_type == "invalid_dependency"

def test_dstt_validator():
    val = DsttValidator()
    
    # Success
    val.validate({
        "segments": [
            {"outputs": ["item_1"]},
            {"outputs": ["item_2"], "is_milestone": True}
        ]
    })
    
    # Missing explicit output definitions entirely
    with pytest.raises(ValidationError) as exc1:
        val.validate({
            "segments": [{"name": "Step 1"}]
        })
    assert exc1.value.error_type == "missing_outputs"
    assert exc1.value.location == "segments[0]"
    
    # Milestone Discipline validation targeting milestone bounds missing variables
    with pytest.raises(ValidationError) as exc2:
        val.validate({
            "segments": [
                {"outputs": [], "is_milestone": True}
            ]
        })
    assert exc2.value.error_type == "milestone_discipline"
