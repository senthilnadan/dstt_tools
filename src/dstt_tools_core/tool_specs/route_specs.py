ROUTE_SPECS = [
    {
        "name": "route.sequence",
        "description": "Routes execution to a sequence of steps",
        "domain": "route",
        "inputs": [{"name": "steps", "type": "array"}],
        "outputs": [{"name": "next_dstt", "type": "string"}],
        "determinism": "deterministic",
        "side_effects": False
    },
    {
        "name": "route.switch",
        "description": "Routes execution based on predicate outcome",
        "domain": "route",
        "inputs": [
            {"name": "value", "type": "any"},
            {"name": "routes", "type": "map"}
        ],
        "outputs": [
            {"name": "next_dstt", "type": "string"}
        ],
        "determinism": "deterministic",
        "side_effects": False
    }
]
