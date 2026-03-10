# DSTT Router Library

## Purpose

The Router Library provides tools that determine **which DSTT should execute next** after a milestone.

Routers sit **outside the DSTT kernel** and operate on milestone outputs.

A router evaluates a milestone state and returns one of:

* the next DSTT
* a routing decision
* a terminal state

Routers never modify execution history.
They only determine the **next step**.

---

# Router Categories

Routers are divided into two fundamental classes:

## 1. Deterministic Routers

Deterministic routers produce the same routing decision given identical inputs.

They remain inside the **deterministic computation realm**.

These routers behave like classical program control flow.

Examples:

* switch
* lookup
* state transition tables
* rule-based routing

---

## 2. Exploratory Routers

Exploratory routers may produce different routing decisions for the same inputs.

They operate in the **reasoning or planning domain**.

Examples:

* LLM-based planners
* heuristic exploration
* search strategies
* probabilistic routing

---

# Deterministic Router Tools

## 1. State Router

Routes based on the value of a state variable.

### Interface

```
route_by_state(state, routes) → dstt
```

### Example

```
routes = {
    "success": success_dstt,
    "retry": retry_dstt,
    "fail": fail_dstt
}
```

Execution:

```
route_by_state("success", routes)
```

Result:

```
success_dstt
```

---

## 2. Predicate Router

Routes based on evaluating predicates.

### Interface

```
route_by_predicate(state, predicates) → dstt
```

### Structure

```
[
  { predicate: p1, dstt: dstt1 },
  { predicate: p2, dstt: dstt2 },
  { predicate: default, dstt: dstt3 }
]
```

Execution stops at the first matching predicate.

---

## 3. Table Router

Uses a routing table keyed by milestone state.

### Interface

```
route_by_table(key, routing_table) → dstt
```

Example:

```
routing_table = {
    "A": dstt_A,
    "B": dstt_B,
    "C": dstt_C
}
```

---

## 4. Sequence Router

Routes to the next DSTT in a predefined sequence.

### Interface

```
route_sequence(sequence, position) → dstt
```

Example:

```
sequence = [dstt_A, dstt_B, dstt_C]
```

---

# Exploratory Router Tools

Exploratory routers are used when the correct next path is **not predetermined**.

They rely on reasoning, heuristics, or search.

These routers may use LLMs.

---

## 1. Planner Router

Uses reasoning to choose the next DSTT.

### Interface

```
plan_next(state, candidate_dstts) → dstt
```

Inputs:

* milestone state
* candidate DSTTs

The router selects the most appropriate DSTT.

---

## 2. Heuristic Router

Uses scoring functions to select the next path.

### Interface

```
route_by_score(state, candidates, scoring_function) → dstt
```

Example scoring criteria:

* estimated cost
* success probability
* tool availability

---

## 3. Exploration Router

Used in search-style systems.

### Interface

```
explore_routes(state, candidate_dstts) → dstt
```

Possible strategies:

* breadth-first
* depth-first
* novelty search
* heuristic exploration

---

# Router Output Contract

Every router must return one of:

```
{
  "next_dstt": DSTT_REFERENCE
}
```

or

```
{
  "terminal_state": RESULT
}
```

---

# Router Execution Model

```
DSTT execution
      ↓
milestone reached
      ↓
router evaluates state
      ↓
next DSTT selected
      ↓
new execution instance starts
```

Routers never reopen closed DSTT segments.

---

# Deterministic Guarantee

Deterministic routers must satisfy:

```
route(state) = same result for same state
```

Exploratory routers are allowed to violate this.

---

# Example Flow

```
DSTT_A
  milestone: result

router → route_by_state(result)

if result == success
    → DSTT_B

if result == retry
    → DSTT_A_retry

if result == fail
    → terminal
```

---

# Role in the DSTT Ecosystem

Routers enable construction of higher-level systems:

* multi-step workflows
* recovery strategies
* search processes
* reasoning pipelines
* exploration systems

DSTT remains purely deterministic while routers manage branching decisions.

---

# Summary

The Router Library provides two complementary capabilities:

Deterministic routers
→ classical control flow

Exploratory routers
→ reasoning and search

Together they enable flexible execution pipelines while preserving the simplicity and determinism of the DSTT kernel.
