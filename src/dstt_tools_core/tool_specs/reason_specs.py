REASON_SPECS = [
    {
        "name": "reason.run",
        "description": "Execute reasoning using a ReasonSpec strategy",
        "domain": "reason",
        "inputs": [
            {"name": "spec_id", "type": "string"},
            {"name": "inputs", "type": "object"}
        ],
        "outputs": [
            {"name": "result", "type": "any"}
        ],
        "determinism": "reasoning",
        "side_effects": False
    },
    {
        "name": "reason.ask_oracle",
        "description": "Escape hatch for raw non-deterministic evaluation",
        "domain": "reason",
        "inputs": [
            {"name": "prompt", "type": "string"}
        ],
        "outputs": [
            {"name": "result", "type": "string"}
        ],
        "determinism": "reasoning",
        "side_effects": False
    },
    {
        "name": "capability.resolve",
        "description": "Resolves whether a task is satisfiable given an inventory of tools",
        "domain": "reason",
        "inputs": [
            {"name": "task", "type": "string"},
            {"name": "tool_inventory", "type": "array"}
        ],
        "outputs": [
            {"name": "filtered_tools", "type": "array"},
            {"name": "missing_capabilities", "type": "array"},
            {"name": "satisfiable", "type": "boolean"}
        ],
        "determinism": "reasoning",
        "side_effects": False
    }
]
