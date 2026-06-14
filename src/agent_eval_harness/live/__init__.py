"""Live architecture invocations (real systems under test).

These build `AgentInvoke` callables that talk to running agents — e.g. a deployed
Wayfinder over HTTP. Kept in a subpackage with optional deps (`[live]`) so the
core framework imports without them.
"""
