The DSTT runtime must be fully deterministic.

All components except reasoning resources MUST produce
identical outputs for identical inputs.

The only permitted source of nondeterminism is the
explicit reasoning operation invoked through reason.run
or equivalent reasoning tools.

No other component may introduce hidden randomness
or adaptive behavior.