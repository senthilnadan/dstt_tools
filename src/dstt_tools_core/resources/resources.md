# DSTT Resource Registry Specification

## Purpose

The Resource Registry provides a stable mechanism to register, discover, and retrieve external execution resources used by DSTT tools.

Resources represent execution engines such as:

* language models
* solvers
* search systems
* data sources
* external APIs

The registry decouples **tools** from specific resource implementations.

---

# Design Principles

1. **Resources are external execution engines**

   Tools call resources to perform work.

2. **DSTT determines resource selection**

   Resource choice must be explicit in DSTT state or inputs.

3. **Registry must remain simple**

   The registry does not perform routing, scheduling, or reasoning.

4. **Resources are identified by namespaced identifiers**

   Example:

```
model.qwen2.5
model.phi3
solver.sat
search.web
dataset.finance
```

---

# Resource Identity

Each resource must have a globally unique identifier.

Format:

```
<domain>.<name>
```

Examples:

```
model.qwen2.5
model.phi3
solver.sat
search.web
dataset.finance
```

The domain indicates the resource class.

---

# Resource Domains

Typical domains include:

```
model
solver
search
dataset
memory
api
```

Systems may introduce additional domains as needed.

---

# Resource Interface

Resources must expose a minimal execution interface.

Example:

```
execute(input)
```

Specific resource types may define additional methods.

Examples:

```
model.generate(prompt)
solver.solve(problem)
search.query(query)
dataset.fetch(key)
```

Tools interacting with resources must understand the specific interface.

The registry itself does not enforce resource behavior.

---

# Core Registry Operations

The registry must support the following operations.

## register

Register a resource with the system.

```
register(name, resource)
```

Example:

```
registry.register("model.qwen2.5", qwen_client)
registry.register("solver.sat", sat_solver)
```

---

## get

Retrieve a resource by identifier.

```
get(name)
```

Example:

```
model = registry.get("model.qwen2.5")
```

If the resource does not exist, the registry must raise an error.

---

## list

List registered resources.

```
list()
```

Returns:

```
["model.qwen2.5", "model.phi3", "solver.sat"]
```

---

## list_by_domain

List resources belonging to a domain.

```
list_by_domain(domain)
```

Example:

```
registry.list_by_domain("model")
```

Returns:

```
["model.qwen2.5", "model.phi3"]
```

---

# Resource Metadata (Optional)

Resources may optionally include metadata.

Example:

```
{
  "name": "model.qwen2.5",
  "domain": "model",
  "provider": "local",
  "capabilities": ["reasoning", "planning"]
}
```

Metadata can assist planners in selecting resources.

The registry itself does not interpret metadata.

---

# Registry Scope

The registry operates at **runtime scope**.

Typical system startup sequence:

```
initialize resource registry
register resources
initialize tool provider
start DSTT execution
```

The registry may be injected into tools during initialization.

---

# Example Usage

Resource registration:

```
registry.register("model.qwen2.5", QwenClient())
registry.register("model.phi3", PhiClient())
registry.register("solver.sat", SatSolver())
```

Reasoning tool execution:

```
model = registry.get("model.qwen2.5")
result = model.generate(prompt)
```

---

# Registry Responsibilities

The registry **does**:

* store resources
* retrieve resources
* expose resource discovery

The registry **does not**:

* schedule resources
* load resources automatically
* perform reasoning
* manage tool logic

---

# Relationship With Tools

Tools interact with the registry to obtain resources.

Example reasoning tool:

```
resource = registry.get(model_id)
result = resource.generate(prompt)
```

DSTT execution remains unaware of the registry.

---

# Relationship With DSTT

DSTT references resources through state.

Example DSTT transition:

```
tool: reason.ask
inputs: [model_id, prompt]
outputs: [response]
```

State:

```
model_id = "model.qwen2.5"
```

---

# Summary

The Resource Registry provides a simple and stable abstraction for accessing execution resources used by DSTT tools.

Responsibilities:

* resource registration
* resource discovery
* resource retrieval

The registry intentionally avoids introducing intelligence or scheduling logic.
