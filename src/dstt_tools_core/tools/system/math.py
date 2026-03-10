from typing import Any
from dstt_tools_core.tools import NativeTool

def math_add(a: Any, b: Any) -> Any:
    return float(a) + float(b)

def math_subtract(a: Any, b: Any) -> Any:
    return float(a) - float(b)

def math_multiply(a: Any, b: Any) -> Any:
    return float(a) * float(b)

def math_divide(a: Any, b: Any) -> Any:
    if float(b) == 0:
        raise ValueError("Cannot divide by zero")
    return float(a) / float(b)

def register_math_tools(registry: Any, namespace_prefix: str = "math"):
    """
    Registers basic arithmetic operations for reasoning evaluation engines globally.
    """
    registry.register(f"{namespace_prefix}.add", NativeTool(math_add))
    registry.register(f"{namespace_prefix}.subtract", NativeTool(math_subtract))
    registry.register(f"{namespace_prefix}.multiply", NativeTool(math_multiply))
    registry.register(f"{namespace_prefix}.divide", NativeTool(math_divide))
