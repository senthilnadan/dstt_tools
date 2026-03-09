# DSTT Tools

## Reasoning Contract

To maintain a strict boundary between deterministic execution and non-deterministic intent interpretation, the following rules apply:

1. **Reasoning via DSTT Only:** All reasoning operations during tool execution MUST occur through DSTT transitions. (Exception: Top-level orchestrators like `ToolRunner` may explicitly invoke `reason.*` tools outside the kernel to bootstrap the initial DSTT graph).
2. **Explicit Tool Definitions:** Tools must not invoke reasoning resources directly unless they are explicitly defined as reasoning tools (e.g., `reason.*`).
3. **No Implicit Reasoning:** ToolProviders must not introduce implicit reasoning behavior natively.
