# Capability Resolution Specification (CapabilitySpec)

Capability resolution determines whether a user task can be executed using the currently available tool ecosystem and identifies any missing capabilities.

This stage occurs **before planning**.

It performs the following functions:

1. Discover relevant tools
2. Filter irrelevant tools
3. Identify missing capabilities
4. Determine if the task is satisfiable
5. Produce a curated tool inventory for planning

---

# Architecture Position


User Task
↓
Capability Resolver
↓
Planner
↓
Enhancer
↓
Validator
↓
DSTT Kernel


Capability resolution **does not build DSTT**.

It only produces a **curated tool inventory**.

---

# Core Principle

Capability resolution must answer:


Can the task be solved using the current tool ecosystem?


Possible outcomes:


SATISFIABLE
PARTIALLY SATISFIABLE
UNSATISFIABLE


---

# CapabilitySpec Structure

```json
{
  "operation": "resolve_capabilities",

  "inputs": {
    "task": "string",
    "tool_inventory": "list"
  },

  "outputs": {
    "filtered_tools": "list",
    "missing_capabilities": "list",
    "satisfiable": "boolean"
  }
}
Resolution Pipeline

Capability resolution executes these steps:

resolve_capabilities_for_task(task)

    ↓

search_tools(task)

    ↓

filter_irrelevant_tools(tools, task)

    ↓

infer_missing_capabilities(filtered_tools, task)

    ↓

determine_satisfiability(filtered_tools, missing_capabilities, task)

    ↓

return CapabilityResult
CapabilityResult
{
  "task": "...",

  "filtered_tools": [
      "math.add",
      "math.multiply",
      "router.switch"
  ],

  "missing_capabilities": [
      "web.search"
  ],

  "satisfiable": true
}
Step 1 — Tool Search

Purpose:

Locate tools potentially relevant to the user task.

search_tools(task)

Implementation strategies:

semantic similarity

tool description matching

keyword extraction

reasoning model

Example:

task: "Compute (a + b) * c"

candidate tools:

math.add
math.multiply
web.search
file.write
router.switch
Step 2 — Tool Filtering

Remove tools irrelevant to the task.

filter_irrelevant_tools(tools, task)

Example:

filtered_tools:

math.add
math.multiply
Step 3 — Missing Capability Inference

Identify capabilities required by the task but not available.

infer_missing_capabilities(filtered_tools, task)

Example:

task: "Find cheapest laptop online"

missing capability:

web.search

Result:

missing_capabilities = ["web.search"]
Step 4 — Task Satisfiability

Determine if the task can be solved with current tools.

determine_satisfiability(tools, missing_capabilities)

Rules:

if missing_capabilities empty → satisfiable

if missing_capabilities exist but constructible → partially satisfiable

if missing_capabilities impossible → unsatisfiable
Capability Categories

Capabilities may belong to domains:

math.*
web.*
file.*
reason.*
route.*
iterate.*
data.*
system.*

Capability inference may operate on domains rather than specific tools.

Example:

missing_capabilities = ["web.search"]

not

missing_capabilities = ["bing.search_tool_v3"]
Integration With Reasoning

Capability resolution may use reasoning tools.

Example DSTT step:

reason.run(
    spec="capability_resolution",
    inputs={
        "task": user_task,
        "tools": tool_inventory
    }
)

The reasoning model produces:

filtered_tools
missing_capabilities
satisfiable
Output Contract for Planner

Planner receives:

{
  "task": "...",
  "tools": ["filtered_tools"]
}

Planner must only use tools in this list.

Planner Constraint

Planner is forbidden from inventing tools.

RULE:

planner_tools ⊆ filtered_tools
Tool Procurement

If missing capabilities exist:

construct_missing_tools(missing_capabilities)

Possible outcomes:

• build new tool
• fetch tool from external registry
• reject task
Capability Resolver Tool

DSTT tool name:

capability.resolve

Signature:

inputs:
  task
  tool_inventory

outputs:
  filtered_tools
  missing_capabilities
  satisfiable
Determinism

Capability resolution is non-deterministic reasoning.

DSTT must treat it as:

reasoning tool

NOT deterministic computation.

Example

User task:

Compute ((a + b) * (c - b)) + ((a - b) * d)

Input tools:

math.add
math.subtract
math.multiply
web.search
file.write

Output:

filtered_tools:

math.add
math.subtract
math.multiply

missing_capabilities:

[]

satisfiable:

true

Planner now builds DAG using only these tools.

Design Constraints

Capability resolution must:

• not generate DSTT
• not execute tools
• not modify tools
• only analyze capability space
Future Extensions

Possible future features:

capability scoring
tool reliability metrics
usage frequency
cost models
parallel tool selection
Summary

Capability resolver prepares the tool universe for planning.

It ensures:

planner works in a constrained environment
LLM reasoning space is reduced
DSTT generation becomes reliable
Role In DSTT Ecosystem
Capability Resolver → prepares tools
Planner → builds DAG
Enhancer → converts DAG → DSTT
Validator → checks correctness
Kernel → executes
Key Principle

DSTT planning must operate only on validated capabilities.

This prevents planners from inventing impossible tools.


---

If you'd like, the **next spec worth writing** (and it will make your planner dramatically stronger) is: