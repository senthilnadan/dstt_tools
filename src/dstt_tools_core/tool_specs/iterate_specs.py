ITERATE_SPECS = [
    {
        "name": "iterate.map",
        "description": "Maps over a sequence of items applying a transition",
        "domain": "iterate",
        "inputs": [
            {"name": "items", "type": "array"},
            {"name": "action_spec", "type": "object"}
        ],
        "outputs": [
            {"name": "results", "type": "array"}
        ],
        "determinism": "deterministic",
        "side_effects": False
    },
    {
        "name": "iterate.reduce",
        "description": "Reduces a sequence of items into a single accumulated state",
        "domain": "iterate",
        "inputs": [
            {"name": "items", "type": "array"},
            {"name": "initial_state", "type": "any"},
            {"name": "action_spec", "type": "object"}
        ],
        "outputs": [
            {"name": "result", "type": "any"}
        ],
        "determinism": "deterministic",
        "side_effects": False
    },
    {
        "name": "iterate.find",
        "description": "Finds the first item matching a predicate sequentially",
        "domain": "iterate",
        "inputs": [
            {"name": "items", "type": "array"},
            {"name": "predicate_spec", "type": "object"}
        ],
        "outputs": [
            {"name": "result", "type": "any"}
        ],
        "determinism": "deterministic",
        "side_effects": False
    },
    {
        "name": "iterate.collect",
        "description": "Collects all items matching a predicate mapping into an array",
        "domain": "iterate",
        "inputs": [
            {"name": "items", "type": "array"},
            {"name": "predicate_spec", "type": "object"}
        ],
        "outputs": [
            {"name": "results", "type": "array"}
        ],
        "determinism": "deterministic",
        "side_effects": False
    }
]
