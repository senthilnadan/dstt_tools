import pytest
from dstt_tools_core.registry import Registry
from dstt_tools_core.provider import Provider
from dstt_tools_core.tools import NativeTool, CompositeTool
from dstt_kernel.kernel import DsttKernal

# --- Mock Library ---
def multiply(a, b):
    return a * b

# --- Setup Fixtures ---
@pytest.fixture
def registry():
    reg = Registry()
    
    # 1. Register the native tools
    reg.register("library.multiply", NativeTool(multiply))
    return reg

@pytest.fixture
def provider(registry):
    return Provider(registry)

# --- Tests ---

def test_execute_single_as_named_segment(registry, provider):
    square_dstt = {
        "segments": [
            {
                "transitions": [
                    {
                        "id": "t1",
                        "tool": "library.multiply",
                        "inputs": ["x", "x"],
                        "outputs": ["product"]
                    }
                ],
                "milestone": ["product"]
            }
        ]
    }
    
    # In the reference test, `tool_provider_instance` was directly passed to `kernal.execute`.
    # Here, we test using the Kernel directly with our wrapped Provider.
    kernal = DsttKernal()
    result = kernal.execute(square_dstt, provider, initial_state={"x": 5})
    assert result == {"product": 25}

    # Now verify that our `CompositeTool` can natively wrap this DSTT and resolve correctly
    square_tool = CompositeTool(square_dstt, provider)
    registry.register("library.square_dstt", square_tool)
    
    # The `get_signature` should expose exactly the one unknown input "x", not "product"
    sig = square_tool.get_signature()
    assert sig["inputs"] == ["x"]
    assert sig["outputs"] == ["product"]
    
    # Execute through the Tool abstraction directly
    wrapped_result = square_tool.execute(5)
    assert wrapped_result == 25


def test_execute_multiple_segments_as_named_segment(registry, provider):
    # First, register the dependency 'square_dstt' as a sub-tool
    square_dstt = {
        "segments": [
            {
                "transitions": [
                    {
                        "id": "t1",
                        "tool": "library.multiply",
                        "inputs": ["x", "x"],
                        "outputs": ["product"]
                    }
                ],
                "milestone": ["product"]
            }
        ]
    }
    square_tool = CompositeTool(square_dstt, provider)
    registry.register("library.square_dstt", square_tool)
    
    # Create the higher level DSTT that utilizes the DSTT sub-tool
    fourthpower_dstt = {
        "segments": [
            {
                "transitions": [
                    {
                        "id": "t1",
                        "tool": "library.square_dstt",
                        "inputs": ["x"],
                        "outputs": ["product"]
                    },
                    {
                        "id": "t2",
                        "tool": "library.square_dstt",
                        "inputs": ["product"],
                        "outputs": ["fourthpower"]
                    }
                ],
                "milestone": ["fourthpower"]
            }
        ]
    }
    
    # Verify execution via Kernel
    kernal = DsttKernal()
    result = kernal.execute(fourthpower_dstt, provider, initial_state={"x": 5})
    assert result == {"fourthpower": 625}

    # Verify execution natively through our framework
    fourthpower_tool = CompositeTool(fourthpower_dstt, provider)
    registry.register("library.fourthpower_dstt", fourthpower_tool)
    
    sig = fourthpower_tool.get_signature()
    assert sig["inputs"] == ["x"]  # "product" shouldn't be here since it's internally produced
    assert sig["outputs"] == ["fourthpower"]
    
    wrapped_result = fourthpower_tool.execute(5)
    assert wrapped_result == 625
