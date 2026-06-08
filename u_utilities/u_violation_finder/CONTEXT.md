# Utility: u_violation_finder

## Purpose
`u_violation_finder` detects denial-constraint violations and returns them as a compressed conflict graph. It is optimized to work on **CompactData** representations.

## Inputs
- `data`: a `pandas.DataFrame` or a `u_shared.Dataset`.
- `dcs`: a `DenialConstraints` object from `u_shared` (optional if `data` is a `Dataset`).

## Outputs
- `ViolationSet`: a compressed violation graph containing `ConflictBlock` entries when rows or clusters violate a constraint.

## Public API
```python
from u_utilities.u_violation_finder import ViolationFinder

finder = ViolationFinder()

# Using a Dataset (most efficient - uses internal compaction)
violations = finder.find_violations(my_dataset)

# Using a raw DataFrame
violations = finder.find_violations(df, dcs)
```

## Design
- `ViolationFinder`: facade that coordinates constraint checks.
- `CompactData`: (in `u_shared`) holds the deduplicated representation used for scanning.
- `ValueGroupedEngine`: exact denial-constraint checker over compact clusters.
- `VectorizedPredicateEvaluator`: NumPy predicate evaluation over bounded row-cluster blocks.

The full reimplementation blueprint lives in `src/internal_readme.md`.
