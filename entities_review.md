# Code Review: `src/entities`

## Overview
The `entities` package provides the core data models for the research framework. Overall, the implementation is clean and leverages modern Python features like `dataclasses`. However, there are some structural rigidities and documentation inconsistencies that should be addressed.

---

## 1. `dataset.py`

### Observations
- **Design Pattern**: The `Dataset` entity centralizes both data storage and violation detection.
- **Inline Imports**: `get_violations` uses an inline import of `ViolationFinder`. While this avoids circular dependencies, it indicates a tight coupling between data entities and processing logic.
- **Caching**: The `get_violations` method does not cache results. This ensures accuracy during iterative repair but has performance implications.

### Suggestions
- **Decouple Finder**: Consider moving violation finding logic out of the entity and into a service/orchestrator to keep entities "anemic" and easier to test in isolation.
- **Clarify `mappings`**: The `mappings` field in `Dataset` is unused and undocumented. Either remove it or document its purpose. [RESOLVED]

---

## 2. `denial_constraints.py`

### Observations
- **Logical Hierarchy**: The structure from `Side` to `DenialConstraints` is well-designed and maps perfectly to the mathematical definition of DCs.
- **String Representation**: `Predicate.to_string` handles DuckDB/SQL formatting. The heuristic for quoting values (`try: float(s.attr)`) is clever but potentially brittle for string values that look like numbers.

### Suggestions
- **Stronger Typing**: `Side.attr` currently holds both attribute names and literal values. Using a more explicit structure or a Union type could improve clarity.
- **Robust Quoting**: Instead of a heuristic, consider storing the original type of the literal value to determine if quotes are needed.

---

## 3. `marginal.py`

### Observations
- **Hardcoded Arity**: The `Marginal` class is strictly 2-way (`attr1`, `attr2`). This is the most significant limitation in the current entity design.
- **Immutability**: Using `frozen=True` is a great practice here.

### Suggestions
- **Generalize Arity**: Refactor `Marginal` to use a list of attributes and values. This would allow the system to support 1-way, 2-way, or N-way marginals without changing the core entity. [RESOLVED]
- **Error Metric Stability**: In `calculate_error`, consider adding a small epsilon to the denominator or using a capped relative error to avoid spikes when `freq` is near zero.

---

## 4. `pipeline_result.py`

### Observations
- **Simplicity**: A clean and effective data container.

### Suggestions
- **Expand Metadata**: Explicitly define common metadata keys in the docstring or as optional fields to encourage consistent usage across different pipeline implementations.

---

## 5. General Recommendations

- **Frozen Dataclasses**: Consider making `Dataset` and `DenialConstraint` frozen as well. In a research pipeline, entities should generally be treated as immutable once created to prevent subtle bugs during transformation stages.
- **Type Hints**: Replace `dict` and `List` with more specific types (e.g., `Dict[str, str]`, `List[Predicate]`) where possible to improve IDE support and catch errors early.
- **Documentation**: Ensure `CONTEXT.md` is updated whenever the implementation changes to avoid the "stale documentation" trap.
