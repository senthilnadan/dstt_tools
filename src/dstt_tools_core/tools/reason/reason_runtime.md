# Reason Runtime

## Purpose

The Reason Runtime defines how reasoning operations are executed inside the DSTT ecosystem.

It governs the lifecycle of reasoning execution using ReasonSpecs and ensures deterministic interaction with probabilistic reasoning resources.

The runtime coordinates:

* ReasonSpec resolution
* resource invocation
* output validation
* repair cycles

---

# Runtime Architecture

Reasoning execution follows this structure:

```
DSTT
  → reason.run
  → ReasonSpec
  → Resource Registry
  → Reasoning Resource
  → Validator
  → Result
```

The runtime acts as the coordinator between these components.

---

# Execution Lifecycle

Every reasoning execution follows the same lifecycle:

```
generate
  → validate
  → repair (optional)
  → return
```

---

## Step 1 — Generate

The runtime retrieves the ReasonSpec and invokes the reasoning resource.

```
spec = reasonspec_registry.get(spec_id)

resource = resource_registry.get(spec.resource_id)

prompt = build_prompt(spec, inputs)

result = resource.generate(prompt)
```

If the resource cannot be resolved:

```
ResourceNotFoundError
```

Execution must stop.

Fallback models are not permitted.

---

## Step 2 — Validate

If the ReasonSpec specifies a validator, the output must be validated.

```
validator = validator_registry.get(spec.validator)

validator.validate(result)
```

Validation may check:

* schema structure
* DSTT correctness
* DAG correctness
* tool existence
* milestone discipline

If validation succeeds, the result is returned.

---

## Step 3 — Repair (Optional)

If validation fails and determinism mode is **strict**, a repair cycle begins.

```
repair_spec = spec.repair_spec
```

The runtime invokes:

```
reason.run(repair_spec, {artifact, error})
```

The repaired artifact is validated again.

The cycle repeats until:

```
valid result
```

or

```
repair limit reached
```

---

# Determinism Modes

ReasonSpecs define determinism behavior.

## strict

Validation is mandatory.

Failure triggers repair.

Typical uses:

```
planning
DSTT generation
structured reasoning
```

---

## relaxed

Validation is optional.

Outputs may vary.

Typical uses:

```
chat
exploration
lab experimentation
```

---

# Error Handling

The runtime must fail explicitly when:

```
ReasonSpec not found
resource not found
validator not found
repair limit exceeded
```

Silent fallback behavior is not permitted.

---

# Repair Limits

The runtime should enforce a repair limit to avoid infinite repair cycles.

Example:

```
max_repair_attempts = 3
```

After exceeding this limit:

```
ReasonExecutionError
```

---

# Observability

The runtime may emit events for tracing.

Examples:

```
reason.generate
reason.validate
reason.repair
reason.complete
```

Tracing systems such as Books or external tracers may subscribe to these events.

---

# Runtime Responsibilities

The Reason Runtime is responsible for:

* executing ReasonSpecs
* coordinating reasoning resources
* validating outputs
* invoking repair when required

The runtime does not:

* modify DSTT
* maintain conversation state
* select reasoning strategies

These responsibilities belong to planners or higher-level orchestration.

---

# Summary

The Reason Runtime ensures controlled reasoning execution through a deterministic lifecycle.

```
generate
 → validate
 → repair
 → return
```

This mechanism allows DSTT to safely incorporate probabilistic reasoning while maintaining deterministic execution boundaries.
