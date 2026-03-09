# DSTT Runner Specification

## Purpose

The Runner is a minimal execution shell responsible for bootstrapping the DSTT ecosystem.

It does **not perform reasoning** itself.

All reasoning must occur inside DSTT segments executed by the kernel.

The Runner only:

1. Initializes system registries
2. Selects the planning strategy
3. Executes the first DSTT
4. Returns the final execution state

---

# Architectural Principles

The Runner must follow these invariants:


Kernel executes DSTT only
Reasoning occurs only inside DSTT transitions
Runner never invokes reasoning tools directly
Strategies are implemented as DSTT artifacts


The Runner acts only as a **system bootstrap layer**.

---

# System Components

The Runner initializes the following system boundaries:

## Kernel

Responsible for deterministic execution.


DsttKernel.execute(dstt, provider, state)


The kernel must not perform reasoning.

---

## Tool Registry

Contains executable tool implementations.

Examples:


math.add
math.subtract
math.multiply
iterate.items
reason.run
capability.resolve


---

## ToolSpec Registry

Provides static metadata about tools.

Used by planners to understand tool capabilities.

Example entry:


{
"name": "math.add",
"inputs": ["a", "b"],
"outputs": ["result"]
}


---

## Resource Registry

Provides access to reasoning resources.

Examples:


model.default_planner
model.analysis
solver.sat
search.web


---

## ReasonSpec Registry

Loads reasoning specifications from YAML files.

These define how reasoning tools behave.

Example:


/lib/reason/specs/plan_arithmetic.yaml


---

## Provider

The Provider connects the kernel to the tool registry.


Provider.execute_transition(tool_name, inputs)


---

# Execution Pipeline

The Runner performs the following steps.

---

## Step 1 — Resolve Tool Universe

The runner collects the available tool definitions.


available_tools = tool_spec_registry.get_all()
available_resources = resource_registry.list()


---

## Step 2 — Select Planning Strategy

The first DSTT is used to determine which planning strategy should be used.


bootstrap_strategy_dstt = provider.load_dstt(
"reason.plan.strategySelect"
)


Initial state passed to the kernel:


{
"task": user_task,
"tools": available_tools
}


Kernel execution:


planner_dstt_name = kernel.execute(
bootstrap_strategy_dstt,
provider,
state
)


The result must contain the selected planner DSTT name.

---

## Step 3 — Load Planner DSTT

The selected planner DSTT is retrieved.


planner_dstt = provider.load_dstt(planner_dstt_name)


---

## Step 4 — Prepare Execution State

The execution state includes:


{
"task": task,
"tools": available_tools,
"resources": available_resources,
"dstt_schema": DSTT_SCHEMA,
...user_input_state
}


---

## Step 5 — Execute Planner DSTT

The planner DSTT generates the execution DSTT.


execution_state = kernel.execute(
planner_dstt,
provider,
state
)


---

## Step 6 — Return Final State

The runner returns the terminal state produced by the kernel.


return execution_state


---

# DSTT Schema Injection

The runner provides the DSTT schema to reasoning tools.

This allows the LLM to generate valid DSTT structures.

Example schema:


{
"segments": [
{
"transitions": [
{
"id": "string",
"tool": "string",
"inputs": ["string"],
"outputs": ["string"]
}
],
"milestone": ["string"]
}
]
}


---

# Strategy Model

Strategies are implemented as DSTT artifacts.

Examples:


reason.plan.strategySelect
reason.plan.arithmetic
reason.plan.iteration
reason.plan.general


Strategies may evolve over time.

However:


Strategies must always be DSTT
Strategies must be executed by the kernel


---

# Runner Responsibilities

The runner is responsible only for:


bootstrap system registries
resolve tool universe
select strategy
execute initial DSTT
return final state


The runner must **not**:


perform reasoning
modify DSTT
call LLMs directly


---

# Future Extensions

Possible future improvements:


tracing support
execution logging
streamed milestone observation
multi-strategy orchestration


These features must **not modify kernel determinism**.

---

# Summary

The Runner is a minimal orchestration shell.


Runner → Kernel → DSTT → Tools → Result


All reasoning is encapsulated within DSTT transitions.

The runner only bootstraps the system.