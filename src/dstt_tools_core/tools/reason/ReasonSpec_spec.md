# ReasonSpec Tool Specification

## Purpose

`ReasonSpec` defines the structured schema for reasoning requests executed within the DSTT kernel. It standardizes the format for how tools in the `reason.*` namespace declare dependencies, expectations, and fallback behaviors natively, enabling planners and validators to uniformly trace reasoning steps.

---

# Identity 

The schema acts as the internal configuration payload bound to any reasoning segment.

```
schema: ReasonSpec
```

---

# Architecture Rules

1. **Explicit Resource Failure**: Resource lookup must fail if the model is missing. No fallback models.
2. **Abstracted Prompts**: `ReasonSpec` defines the reasoning strategy. Tools must not embed hardcoded prompts.
3. **Minimal Parsing**: Parsing should remain minimal (JSON, object schema, or plain text).
4. **Separation of Concerns**: Structural validation should be performed by validators, not parsers.
5. **Delegated Healing**: Repairs should be handled by `reason.repair` instead of complex inline parsing logic.

---

# Structure

A complete `ReasonSpec` configures a reasoning boundary. It allows the execution kernel—or external evaluation tools—to inspect the prompt constraints, required return shapes, and resource designations.

```json
{
  "mode": "ask | ask_structured | score | plan | repair",
  "resource_domain": "model | solver | search",
  "resource_id": "model.qwen2.5",
  "context": {
    "task": "...",
    "tools": ["...", "..."],
    "constraints": ["..."]
  },
  "schema_target": {
    "type": "object",
    "properties": { "...": "..." }
  },
  "determinism": "strict | relaxed"
}
```

---

# Fields

### mode

The specific `reason.*` tool variation being requested.

Enum:
- `ask`: Free-form text resolution
- `ask_structured`: Strictly parsed JSON structure matching `schema_target`
- `score`: Candidates evaluation and ranking
- `plan`: Strategic workflow graph formulation
- `repair`: Healing execution targeting broken constraints

### resource_domain

The domain family expected to fulfill this reasoning request safely, aligning with the `ResourceRegistry`.

Enum:
- `model`: Language models (LLMs)
- `solver`: SAT solvers or deterministic symbolic engines
- `search`: External retrieval APIs

### resource_id 

The precise identifier mapping to the execution engine.

Example:
```
model.phi3
```

### context

A dynamic dictionary passing state payload into the prompt. It dictates what variables the reasoner has access to. Typical fields include `task` definitions, `tools` arrays, `error` traces (for `repair`), and `candidates` (for `score`). 

### schema_target

When the mode is expected to output a strict object (e.g. `ask_structured`, `plan`, `repair`), this defines the target shape using JSON Schema.

### determinism

Specifies the expected variance in engine outputs.

Enum:
- `strict`: Enforces consistent structuring. Useful for programmatic constraints.
- `relaxed`: Allows conversational or open-ended variation (e.g. code generation, creative formatting).

---

# Integration with DSTT State

`ReasonSpec` payloads are intrinsically tied to specific segment nodes in DSTT structures.

Example representation inside a serialized DSTT state block:

```yaml
segments:
  - id: reason_phase_1
    tool: reason.ask_structured
        inputs:
      - spec: 
          mode: ask_structured
          resource_id: model.qwen2.5
          context:
            task: "Extract names and dates."
          schema_target:
            type: array
            items: 
              type: string
    outputs:
      - extracted_entities
```

---

# Verification Lifecycle

Because reasoning models are technically non-deterministic, `ReasonSpec` defines exactly what MUST be validated after execution.

1. **Resolution Check**: Did the `ResourceRegistry` successfully map `resource_id`? (If missing, execution explicitly fails).
2. **Execution Check**: Did the engine return a payload without timing out?
3. **Schema Validation**: If `schema_target` was defined, does the output perfectly validate against it via an external validator?

If any step fails, the DSTT segment transitions into a `repair` stage using `reason.repair`.

---

# Summary

`ReasonSpec` provides the shared schema enabling:
1. Orchestrators to understand *what* a reasoning block is attempting to do.
2. The `ResourceRegistry` to efficiently marshal the request to the correct payload shape.
3. Validators to cleanly audit the non-deterministic output shapes against their pre-declared targets.


ReasonSpec Storage Format

ReasonSpecs are stored as external configuration documents.

The canonical storage format is YAML.

Each ReasonSpec file defines a single ReasonSpec instance.

Recommended directory structure:

/lib/reason/specs/

Example:

/lib/reason/specs/plan_arithmetic.yaml
/lib/reason/specs/repair_dstt.yaml
ReasonSchema Definition

The ReasonSchema defines the expected structure for reasoning outputs.

A ReasonSpec may optionally reference a ReasonSchema using the schema_target field.

The schema is used to validate structured outputs produced by reasoning resources.

Example ReasonSchema:

{
  "type": "object",
  "properties": {
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "tool": {"type": "string"},
          "inputs": {"type": "array"},
          "outputs": {"type": "array"},
          "deps": {"type": "array"}
        }
      }
    }
  }
}

The ReasonSchema is not enforced by ReasonSpec itself but may be enforced by:

validators
reason.verify tools
external schema validation layers
YAML Mapping Rules

Each YAML ReasonSpec file must map directly to the ReasonSpec structure.

Example:

mode: plan

resource_domain: model

resource_id: model.qwen2.5

context:
  task: "{task}"

schema_target: dag_schema

determinism: relaxed

Mapping rules:

YAML field	ReasonSpec property
mode	Reason operation mode
resource_domain	Resource category
resource_id	Target reasoning resource
context	Runtime context injection
schema_target	Optional structured output schema
determinism	Reasoning determinism expectation
ReasonSpec Identification

Each ReasonSpec is uniquely identified by the file name.

Example:

plan_arithmetic.yaml

becomes:

ReasonSpec ID = "plan_arithmetic"

This identifier is used when invoking reasoning operations:

reason.run("plan_arithmetic", context)