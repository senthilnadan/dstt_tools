# Validator Specification

## Purpose

Validators enforce structural and semantic correctness within the DSTT ecosystem.

They ensure that artifacts generated through reasoning satisfy the constraints required for deterministic execution.

Validators are used by the Reason Runtime to verify outputs produced by reasoning resources.

---

# Design Principles

Validators must follow these principles:

1. **Deterministic**

Validation must produce the same result for identical inputs.

2. **Pure**

Validators must not modify the artifact being validated.

3. **Side-effect free**

Validators must not invoke tools or reasoning resources.

4. **Fail fast**

Validation errors must be returned immediately.

5. **Explainable**

Validation errors must contain sufficient detail for repair operations.

---

# Validation Targets

Validators operate on structured artifacts.

Common targets include:

```id="icjv3m"
DSTT
DAG
Tool Plan
Structured Output
```

Validators verify that artifacts conform to expected schemas and execution rules.

---

# Validator Interface

Validators expose a simple interface.

Example:

```id="a7i4np"
validate(artifact) → success | error
```

If validation succeeds:

```id="q9b5zj"
return True
```

If validation fails:

```id="b1u1p4"
raise ValidationError
```

The error must contain structured feedback.

Example:

```id="tdw3e6"
{
  "error": "missing_milestone",
  "segment": 2,
  "detail": "segment must declare milestone outputs"
}
```

---

# Validator Registry

Validators are retrieved through a Validator Registry.

Example:

```id="p3lqk1"
validator = validator_registry.get("dstt_validator")
```

Validators are registered during system initialization.

Example:

```id="j2j6b8"
validator_registry.register("dstt_validator", DsttValidator())
```

---

# Common Validators

## dstt_validator

Ensures DSTT artifacts follow execution rules.

Checks may include:

```id="a5c0r5"
valid segment structure
valid transition structure
milestone discipline
unique output names
valid tool references
```

---

## dag_validator

Ensures DAG artifacts are valid.

Checks may include:

```id="vt98dx"
no cycles
valid dependencies
unique node identifiers
valid tool references
```

---

## schema_validator

Ensures structured outputs match schema definitions.

Checks may include:

```id="y5n8fk"
JSON schema validation
required fields present
correct data types
```

---

# Validation Lifecycle

Validators are executed during the reasoning runtime.

Example:

```id="3n6qkp"
generate
 → validate
 → repair
```

If validation succeeds:

```id="z8reiv"
return artifact
```

If validation fails:

```id="x4qjey"
invoke repair ReasonSpec
```

---

# Validation Errors

Validation errors must contain structured data to guide repair.

Example error structure:

```id="k8k8m7"
{
  "error_type": "missing_output",
  "location": "segment[2].transition[1]",
  "message": "transition must declare outputs"
}
```

These errors are passed directly to repair ReasonSpecs.

---

# Repair Interaction

Validators do not attempt repair.

Instead they provide structured feedback used by `reason.repair`.

Example flow:

```id="pqgnyh"
artifact
 → validator
 → validation error
 → reason.repair
 → validator
```

---

# Determinism Enforcement

Validators are critical to enforcing determinism in DSTT.

Artifacts that fail validation must not be executed.

Validators ensure:

```id="i1o5z0"
correct structure
valid execution order
correct tool usage
```

This prevents probabilistic reasoning outputs from corrupting deterministic execution.

---

# Validator Responsibilities

Validators are responsible for:

```id="hzoh0o"
artifact verification
structural validation
error reporting
```

Validators are not responsible for:

```id="2q4u2v"
repairing artifacts
executing tools
generating reasoning
```

---

# Summary

Validators enforce correctness boundaries within the DSTT ecosystem.

They allow probabilistic reasoning to safely produce artifacts that can be executed deterministically.

Execution flow:

```id="qz2v3o"
reasoning
 → validator
 → repair
 → execution
```

Validators ensure that DSTT execution remains safe, reproducible, and structurally correct.
