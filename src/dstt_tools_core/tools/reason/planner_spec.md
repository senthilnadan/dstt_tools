# Planner Specification (PlannerSpec)

PlannerSpec defines the rules and structure used to transform a user task into a Directed Acyclic Graph (DAG) composed of tool operations.

The planner does not execute tools.

It produces a graph representation that will later be converted into a DSTT execution structure.

---

# Planner Position in DSTT Architecture

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

The planner operates after capability resolution and before DSTT generation.

---

# Planner Responsibilities

The planner performs the following operations:

1. Interpret the user task
2. Select tools from the filtered tool inventory
3. Determine dependencies between tool operations
4. Construct a valid DAG
5. Produce graph nodes that can be transformed into DSTT transitions

---

# Planner Input

Planner receives the following payload.

```json
{
  "task": "string",
  "tools": ["tool.name", "tool.name", "..."]
}

Example:

{
  "task": "Compute ((a + b) * (c - b))",
  "tools": [
    "math.add",
    "math.subtract",
    "math.multiply"
  ]
}

The planner must only use tools listed in the input.

Planner Output (DAG)

The planner must produce a Directed Acyclic Graph structure.

{
  "nodes": [
    {
      "id": "t1",
      "tool": "math.add",
      "inputs": ["a", "b"],
      "outputs": ["sum_ab"],
      "deps": []
    },
    {
      "id": "t2",
      "tool": "math.subtract",
      "inputs": ["c", "b"],
      "outputs": ["diff_cb"],
      "deps": []
    },
    {
      "id": "t3",
      "tool": "math.multiply",
      "inputs": ["sum_ab", "diff_cb"],
      "outputs": ["result"],
      "deps": ["t1", "t2"]
    }
  ]
}
Node Definition

Each node must follow this schema.

{
  "id": "unique node identifier",
  "tool": "tool.name",
  "inputs": ["state variables"],
  "outputs": ["state variables"],
  "deps": ["node ids"]
}
Node Rules

The planner must enforce the following constraints.

Rule 1: Tool Validity

The tool used in each node must exist in the provided tool list.

node.tool ∈ planner_input.tools
Rule 2: Dependency Validity

Dependencies must reference earlier nodes.

node.deps ⊆ existing_node_ids
Rule 3: Variable Flow

Inputs must be either:

• task parameters
• outputs of previous nodes

Example:

valid input:
a
b
sum_ab
Rule 4: Unique Outputs

Each output variable should be produced by exactly one node.

Rule 5: Acyclic Graph

The planner must not produce cycles.

Graph must satisfy:

DAG(nodes)
Planner Constraints

The planner must never:

• invent tools
• invent capabilities
• reference unknown variables
• create cycles

Planner Depth Guidance

To prevent overly complex plans, planners should follow this heuristic:

preferred_depth ≤ 3

Large tasks should be decomposed before planning.

Planner Strategy

Planner may use reasoning tools.

Example:

reason.run(
  spec="plan_dag",
  inputs={
    "task": task,
    "tools": tools
  }
)
Planner Failure Modes

Planner may fail if:

• required tools are missing
• task is ambiguous
• DAG cannot be constructed

In such cases it should return:

{
  "error": "planning_failed",
  "reason": "missing_tool"
}
Planner Output Guarantee

Planner output must guarantee:

valid DAG
tool usage constrained to input tools
deterministic dependency structure
DAG → DSTT Conversion

Planner output will be transformed by the enhancer into DSTT segments.

Example transformation:

DAG

t1
t2
↓
t3

becomes

DSTT

Segment 1
t1
t2
milestone: sum_ab, diff_cb

Segment 2
t3
milestone: result

Planner Determinism

Planner itself is a reasoning process.

Planner tools are therefore classified as:

determinism: reasoning
Example Planning Task

User Task

Compute ((a + b) * (c - b)) + ((a - b) * d)

Planner DAG

{
  "nodes": [
    {
      "id": "t1",
      "tool": "math.add",
      "inputs": ["a", "b"],
      "outputs": ["sum_ab"],
      "deps": []
    },
    {
      "id": "t2",
      "tool": "math.subtract",
      "inputs": ["c", "b"],
      "outputs": ["diff_cb"],
      "deps": []
    },
    {
      "id": "t3",
      "tool": "math.multiply",
      "inputs": ["sum_ab", "diff_cb"],
      "outputs": ["prod1"],
      "deps": ["t1", "t2"]
    },
    {
      "id": "t4",
      "tool": "math.subtract",
      "inputs": ["a", "b"],
      "outputs": ["diff_ab"],
      "deps": []
    },
    {
      "id": "t5",
      "tool": "math.multiply",
      "inputs": ["diff_ab", "d"],
      "outputs": ["prod2"],
      "deps": ["t4"]
    },
    {
      "id": "t6",
      "tool": "math.add",
      "inputs": ["prod1", "prod2"],
      "outputs": ["result"],
      "deps": ["t3", "t5"]
    }
  ]
}
Relationship with DSTT

Planner produces DAG.

Enhancer converts DAG → DSTT.

DSTT kernel executes transitions deterministically.

Key Principle

Planner must produce graphs that are:

valid
acyclic
tool constrained
state consistent