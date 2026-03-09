import pytest
from dstt_tools_core.resources.registry import ResourceRegistry

# --- Mock Resources ---
class MockLLM:
    def generate(self, prompt):
        return f"Generated: {prompt}"

class MockSolver:
    def solve(self, problem):
        return f"Solved: {problem}"

class MockSearch:
    def query(self, query):
        return f"Found: {query}"

# --- Fixtures ---
@pytest.fixture
def resource_registry():
    registry = ResourceRegistry()
    registry.register("model.qwen2.5", MockLLM())
    registry.register("model.phi3", MockLLM())
    registry.register("solver.sat", MockSolver())
    registry.register("search.web", MockSearch())
    return registry

# --- Tests ---
def test_resource_retrieval(resource_registry):
    # Test successful retrieval
    qwen = resource_registry.get("model.qwen2.5")
    assert isinstance(qwen, MockLLM)
    assert qwen.generate("hello") == "Generated: hello"

    sat = resource_registry.get("solver.sat")
    assert isinstance(sat, MockSolver)
    assert sat.solve("math") == "Solved: math"

def test_resource_not_found(resource_registry):
    with pytest.raises(ValueError, match="Resource 'model.unknown' not found."):
        resource_registry.get("model.unknown")

def test_list_all_resources(resource_registry):
    all_resources = resource_registry.list()
    assert len(all_resources) == 4
    assert "model.qwen2.5" in all_resources
    assert "model.phi3" in all_resources
    assert "solver.sat" in all_resources
    assert "search.web" in all_resources

def test_list_by_domain(resource_registry):
    # Retrieve models
    models = resource_registry.list_by_domain("model")
    assert len(models) == 2
    assert "model.qwen2.5" in models
    assert "model.phi3" in models
    
    # Retrieve solvers
    solvers = resource_registry.list_by_domain("solver")
    assert len(solvers) == 1
    assert "solver.sat" in solvers
    
    # Missing domain
    empty = resource_registry.list_by_domain("api")
    assert len(empty) == 0
