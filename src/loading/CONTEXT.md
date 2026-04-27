# Loading Context

## Goal
The loading stage is responsible for reading private datasets, metadata, and denial constraints, and identifying all initial violations in the data.

## Violation Detection Algorithm
The system uses a **Hybrid Optimized Violation Finder** that categorizes Denial Constraints (DCs) into structural patterns and selects the most efficient execution engine (Pandas/NumPy or DuckDB) for each.

### Core Strategies

#### 1. Existence Check (Early Exit)
Before generating pairs, the finder performs a rapid check using DuckDB aggregates or Pandas masks. If a constraint is satisfied by all rows, it skips further processing for that DC.

#### 2. Functional Dependencies (FDs & CFDs)
**Engine:** Pandas + NumPy
**Logic:** Identify groups with more than one unique value for the dependent attribute.
**Example:** `not(t1.CIT=t2.CIT & t1.NATIVITY!=t2.NATIVITY)`
```python
# 1. Isolate rows satisfying unary filters
# 2. Identify violating groups
mask = df.groupby('CIT')['NATIVITY'].transform('nunique') > 1
violating_data = df[mask]
# 3. Generate pairs via cross-product within groups
```

#### 3. Constant-Value Implications
**Engine:** Pandas + NumPy
**Logic:** Use boolean indexing to isolate subsets and NumPy broadcasting for comparison.
**Example:** `not(t1.AGEP=0 & t2.AGEP=0 & t1.SCHL=0 & t2.SCHL!=0)`
```python
idx1 = df[df['SCHL'] == 0].index
idx2 = df[df['SCHL'] != 0].index
# Broadcasted comparison (with index safety)
```

#### 4. Order Constraints (OCs)
**Engine:** DuckDB
**Logic:** Uses DuckDB's optimized inequality joins and window functions.
**Example:** `not(t1.State=t2.State & t1.Salary > t2.Salary & t1.Rate < t2.Rate)`
```sql
SELECT t1.idx, t2.idx 
FROM df t1 JOIN df t2 ON t1.State = t2.State
WHERE t1.idx < t2.idx AND t1.Salary > t2.Salary AND t1.Rate < t2.Rate
```

#### 5. Pure Order Constraints
**Engine:** DuckDB
**Logic:** Inequality join directly in the `ON` clause to avoid Cartesian products.
**Example:** `not(t1.gain < t2.gain & t1.loss < t2.loss)`
```sql
SELECT t1.idx, t2.idx 
FROM df t1 JOIN df t2 ON t1.gain < t2.gain
WHERE t1.idx < t2.idx AND t1.loss < t2.loss
```

## Performance Benchmarks (1M+ Rows)
| Pattern | Engine | Runtime (No Violations) | Runtime (1M Violations) |
| :--- | :--- | :--- | :--- |
| FD (A->B) | Pandas | ~0.5s | ~15s |
| OC (Filtered) | NumPy | ~0.1s | ~20s |
| Pure Order | DuckDB | ~0.2s | ~40s |

## Key Components
- **FileLoader**: Orchestrates the loading and encoding of data and constraints.
- **ViolationFinder**: The hybrid execution router.
- **DataEncoder**: Uses `LabelEncoder` to ensure all categorical data is numeric before detection.
- **DCsEncoder**: Rewrites constraints to match encoded numeric values.

## Testing
The loading and violation finding processes are verified by a comprehensive test suite in `tests/loading/`.

### 1. Component Tests (`test_components.py`)
Tests the individual units of the loading pipeline in isolation:
- **`DataLoader`**: Verifies correct CSV reading into Pandas DataFrames.
- **`DCsLoader`**: Validates the parsing logic for Denial Constraints from text files, including unary and binary predicates.
- **`MetadataLoader`**: Ensures JSON metadata is loaded correctly.
- **`DataEncoder`**: Verifies that categorical columns are correctly transformed into numeric codes and that mappings are preserved.
- **`DCsEncoder`**: Validates that literals within Denial Constraints are correctly rewritten to match the encoded data.

### 2. Violation Finder Tests (`test_violation_finder.py`)
Focuses on the logical correctness of the `ViolationFinder` across its three main execution paths:
- **Constant Implication (Pandas Path)**: Verifies detection of violations involving constant values (e.g., `t1.A=v`).
- **Functional Dependency (Value-Partitioned Join)**: Tests the efficient detection of FD violations (e.g., `t1.A=t2.A & t1.B!=t2.B`).
- **Order Constraints (DuckDB Path)**: Validates inequality-based violations using the DuckDB engine (e.g., `t1.Age < t2.Age & t1.Salary > t2.Salary`).
- **Edge Cases**: Ensures correct behavior for empty datasets or constraints with no violations.

### 3. Integration Tests (`test_file_loader.py`)
Tests the full orchestration of the loading stage:
- **`FileLoader` Orchestration**: Loads the project's `dummy` dataset from `data/dummy`, performs encoding, and runs violation discovery in a single flow.
- **End-to-End Validation**: Ensures the resulting `DatasetWithViolations` entity has correctly encoded data, mapped constraints, and a non-empty set of detected violations.
