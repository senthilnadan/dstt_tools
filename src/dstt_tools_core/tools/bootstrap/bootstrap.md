# DSTT Bootstrap Library (Minimal Specification)

## Purpose

The bootstrap library contains DSTT tools used to start the execution pipeline.

Bootstrap DSTTs are executed directly by the kernel and return the name of the planner DSTT that should handle the task.

The runner only triggers the bootstrap DSTT.

All reasoning occurs inside DSTT execution.

---

## Bootstrap Responsibility

Bootstrap DSTTs only perform:

- strategy selection
- initial routing

They must **not**:

- construct execution graphs
- perform planning
- call iterative tools

Those responsibilities belong to planner DSTTs.

---

## Execution Model

Runner execution pipeline:

Runner → Bootstrap DSTT → Planner DSTT → Kernel Execution

Example flow:

1. Runner provides context state:


{
"task": user_task
}


2. Runner executes bootstrap DSTT:


kernel.execute(bootstrap.strategy_select)


3. Bootstrap returns planner name:


{
"planner": "reason.plan.arithmetic"
}


4. Runner loads planner DSTT and executes it.

---

## Bootstrap DSTT Namespace

Bootstrap tools must use the namespace:


bootstrap.*


Examples:


bootstrap.strategy_select
bootstrap.route_task


Initially only one bootstrap DSTT is required.

---

## bootstrap.strategy_select

Purpose:

Select the planner strategy that should handle the user task.

Inputs:


task


Outputs:


planner


Expected output example:


planner = "reason.plan.arithmetic"


---

## Bootstrap Design Rules

Bootstrap DSTTs must remain:

- small
- deterministic
- single-purpose

They should contain **only one segment whenever possible**.

Bootstrap must remain simple so the runner does not become complex.

---

## Library Location

Bootstrap DSTT tools should live in a dedicated library directory.

Example:


lib/bootstrap/


Each bootstrap DSTT is registered as a DSTT tool in the tool provider.

---

## Summary

Bootstrap exists only to start the planning pipeline.


Runner → Bootstrap → Planner → Execution


Bootstrap selects **what planner should run next**, nothing more.