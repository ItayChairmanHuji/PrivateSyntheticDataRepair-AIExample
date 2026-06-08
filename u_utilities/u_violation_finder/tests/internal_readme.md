# Tests: u_violation_finder

## Contract
The test suite verifies the public facade and the active value-grouped engine. Tests use in-memory dataframes and manually constructed denial constraints, so they do not depend on resource paths or filesystem state.

## Coverage
- Public top-level import resolves to the facade.
- Equality-key partitioning finds functional-dependency style violations.
- Nullable equality-key partitioning preserves null groups.
- Internal group checks detect violations between duplicate value-group rows.
- Self-group edge counts are undirected and emitted once.
- Unary literal predicates coerce numeric strings before vectorized comparison.
- Reversed tuple sides are evaluated in both pair orientations.

## Expected Result Shape
Assertions normalize expanded biclique output into undirected row-pair sets. This keeps the tests focused on the violation contract rather than the compressed storage layout.
