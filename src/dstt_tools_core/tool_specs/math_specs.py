MATH_SPECS = [
    {
        "name": "math.add",
        "description": "Add two numbers",
        "domain": "math",
        "inputs": [{"name": "a", "type": "number"}, {"name": "b", "type": "number"}],
        "outputs": [{"name": "sum", "type": "number"}],
        "determinism": "deterministic",
        "side_effects": False
    },
    {
        "name": "math.multiply",
        "description": "Multiply two numbers",
        "domain": "math",
        "inputs": [{"name": "a", "type": "number"}, {"name": "b", "type": "number"}],
        "outputs": [{"name": "product", "type": "number"}],
        "determinism": "deterministic",
        "side_effects": False
    }
]
