# Reasoning Layer

## Purpose

The reasoning layer provides controlled access to external intelligence systems such as language models, solvers, or search engines.

Reasoning is executed deterministically through **ReasonSpec definitions**, ensuring that DSTT execution remains reproducible and structurally stable.

The reasoning system separates:

* execution (DSTT)
* reasoning strategy (ReasonSpec)
* compute resources (Resource Registry)

---

# Design Principles

The reasoning layer must follow these rules:

1. **No embedded prompts**

Reasoning tools must not contain prompts.
All prompts are defined inside ReasonSpecs.

2. **Explicit resource resolution**

Resources must be resolved through the Resource Registry.

If a resource is missing, execution must fail.

Fallback models are not allowed.

3. **Minimal parsing**

Reasoning outputs should be treated as structured data where possible.

Complex parsing logic should not exist inside the reasoning layer.

4. **Validation driven correctness**

Outputs must be validated using external validators.

Validation failures are handled through `reason.repair`.

5. **ReasonSpec driven behavior**

All reasoning behavior is defined by ReasonSpecs rather than tool implementations.

---

# Execution Model

Reasoning execution always follows this structure:

```
DSTT
  → reason.run
  → ReasonSpec
  → Resource Registry
  → Reasoning Resource
  → Output
```

---

# Core Reasoning Tool

## reason.run

Executes reasoning using a ReasonSpec.

### Inputs

```
spec_id
inputs
```

### Behavior

1. Load ReasonSpec
2. Resolve resource from Resource Registry
3. Build prompt from ReasonSpec template
4. Execute reasoning resource
5. Return structured result

Example:

```
reason.run(
  spec_id = "plan_dag",
  inputs = {
    task: "...",
    tools: [...]
  }
)
```

---

# Optional Tool

## reason.ask_oracle

Direct access to a reasoning resource.

This tool bypasses ReasonSpec and is intended only for:

* debugging
* experimentation
* lab exploration

### Inputs

```
resource_id
prompt
schema (optional)
```

### Output

```
response
```

Example:

```
reason.ask_oracle(
  resource_id = "model.qwen2.5",
  prompt = "Explain SAT solving"
)
```

This tool should not be used in production DSTT pipelines.

---

# ReasonSpec Relationship

ReasonSpecs define the reasoning behavior used by `reason.run`.

A ReasonSpec contains:

* reasoning mode
* resource identifier
* prompt template
* input variables
* optional schema definition
* optional validator
* determinism level

Example:

```
plan_dag
repair_dstt
decompose_task
chat_default
```

---

# Determinism Levels

ReasonSpecs specify determinism expectations.

### strict

Output must pass validation.

Failure triggers repair.

Typical uses:

* planning
* repair
* structured generation

---

### relaxed

Output may vary.

Used for exploratory reasoning.

Typical uses:

* chat
* brainstorming
* lab experiments

---

# Validation Lifecycle

Reasoning output should follow the lifecycle:

```
generate
  → validate
  → repair (if required)
```

Repair operations should be handled by `reason.repair` ReasonSpecs.

---

# Summary

The reasoning layer contains only two tools:

```
reason.run
reason.ask_oracle
```

All reasoning behavior is defined externally through ReasonSpecs.

This ensures that:

* reasoning strategies remain configurable
* DSTT execution remains deterministic
* compute resources remain replaceable
* prompts remain externalized
