STRATEGY_SPECS = [
    {
        "name": "reason.plan.strategySelect",
        "description": "Selects the optimal planner based on tools",
        "domain": "reason.plan",
        "segments": [{
            "transitions": [{
                "id": "t1",
                "tool": "reason.run",
                "inputs": ["strategy_spec_id", "strategy_inputs"],
                "outputs": ["planner_dstt_name"]
            }],
            "milestone": ["planner_dstt_name"]
        }]
    },
    {
        "name": "reason.plan.arithmetic",
        "description": "Arithmetic specific planner",
        "domain": "reason.plan",
        "segments": [{
            "transitions": [{
                "id": "t1",
                "tool": "reason.run",
                "inputs": ["plan_spec_id", "plan_inputs"],
                "outputs": ["execution_dstt"]
            }],
            "milestone": ["execution_dstt"]
        }]
    }
]
