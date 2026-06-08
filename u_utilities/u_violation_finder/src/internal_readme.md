# Violation Finder (Optimized Architecture)

This utility finds all pairs of rows in a dataset that violate a set of Denial Constraints (DCs). It uses a multi-engine approach to select the most efficient tool for each specific constraint pattern.

---

## 1. Engine Selection Logic

The `ConstraintAnalyzer` inspects each DC and assigns it to a specialized engine:

| Constraint Type | Pattern Example | Engine | Primary Tool |
| :--- | :--- | :--- | :--- |
| **Functional Dependency (FD)** | `A=A & B!=B` | `FDEngine` | Pandas GroupBy |
| **Conditional Constant** | `A=c1 & B!=B` | `ConditionalConstantEngine` | Pandas GroupBy (Filtered) |
| **Single Order** | `A > A` | `OrderEngine` | NumPy Sorting & Binary Search |
| **Two Order** | `A > A & B < B` | `OrderEngine` | Sorted Filtering (2D Dominance) |
| **General / Complex** | `A=A & B > B & C < C` | `DuckDBEngine` | DuckDB SQL (Optimized Joins) |

---

## 2. Optimizations

### A. Symbolic Representation
Instead of materializing billions of edges, we use `ViolationSet` with:
- **MultiClusterConflict**: Conflicts between sets of clusters.
- **RangeConflict**: Conflicts between a row and a continuous range of sorted indices.
- **ClusterConflict**: Conflicts between two clusters (or a cluster with itself).

### B. FDEngine (Pandas)
Optimized for FD patterns. It groups the dataset by equality keys and then identifies conflicting values of the inequality key within each group. This is $O(N)$ and extremely memory efficient.

### C. OrderEngine (NumPy)
Optimized for ordering rules. It sorts the clusters and uses binary search (`np.searchsorted`) to identify ranges of violating neighbors. It emits `RangeConflict` objects to keep the graph compact. For 2D order constraints, it uses a sorted filtering approach.

### D. DuckDBEngine (Fallback)
Used for everything else. It translates DCs into SQL JOINs. If equality predicates are present, it uses explicit `JOIN ... ON` clauses to leverage DuckDB's hash join optimizations. It also handles `NULL` values correctly using `IS NOT DISTINCT FROM`.

---

## 3. Data Flow

1.  **CompactData**: The dataset is first deduplicated into "Clusters". All engines operate on these clusters to minimize processing overhead.
2.  **Orchestrator**: Coordinates the analysis and dispatching.
3.  **ViolationSet**: Aggregates conflicts from all engines and provides a unified interface for the Repairer.

---

## 4. Pseudo-code for Constraint Types

### A. FDEngine (Functional Dependency)
**Logic**: Identifies violations of the form `t1.A = t2.A & t1.B != t2.B`.

```python
def find_violations_fd(data, eq_attrs, neq_attr):
    # 1. Group by the equality attributes (A=A)
    grouped = data.groupby(eq_attrs)
    
    for _, group_df in grouped:
        # 2. Within each group, group by the inequality attribute (B!=B)
        subgroups = group_df.groupby(neq_attr)
        
        # 3. Every row in one subgroup conflicts with every row in every OTHER subgroup
        subgroup_list = [sub_df.indices for _, sub_df in subgroups]
        for i in range(len(subgroup_list)):
            for j in range(i + 1, len(subgroup_list)):
                report_multi_cluster_conflict(subgroup_list[i], subgroup_list[j])
```

### B. ConditionalConstantEngine
**Logic**: Handles `t1.A = t2.A & t1.B != t2.B` where `t1` and `t2` have specific unary filters (e.g., `t1.C = 'v1'`).

```python
def find_violations_cc(data, eq_attrs, neq_attr, t1_filter, t2_filter):
    # 1. Apply separate filters for t1 and t2
    t1_data = data.filter(t1_filter)
    t2_data = data.filter(t2_filter)
    
    # 2. Group both by equality attributes
    t1_groups = t1_data.groupby(eq_attrs)
    t2_groups = t2_data.groupby(eq_attrs)
    
    # 3. Join groups on common equality keys
    for key in t1_groups.keys() & t2_groups.keys():
        # 4. Within the same equality group, check inequality on B
        t1_sub = t1_groups[key].groupby(neq_attr)
        t2_sub = t2_groups[key].groupby(neq_attr)
        
        for val1, g1 in t1_sub:
            for val2, g2 in t2_sub:
                if val1 != val2:
                    report_multi_cluster_conflict(g1, g2)
```

### C. OrderEngine (Single Order)
**Logic**: Optimized for `t1.A > t2.A`. Uses sorting and binary search.

```python
def find_violations_single_order(data, attr, opr, t1_filter, t2_filter):
    t1_rows = data.filter(t1_filter)
    t2_rows = data.filter(t2_filter).sort_by(attr) # O(N log N)
    
    for row1 in t1_rows:
        # Find the range of rows in t2 that satisfy the operator (e.g., < row1.A)
        # Using binary search (np.searchsorted) is O(log N)
        violation_range = t2_rows.search_range(row1[attr], opr)
        
        if violation_range:
            # Emits a symbolic range conflict to save memory
            report_range_conflict(row1.id, violation_range)
```

### D. OrderEngine (Two Order)
**Logic**: Handles `t1.A > t2.A & t1.B > t2.B`. Uses a sorted filtering approach.

```python
def find_violations_two_order(data, attr1, opr1, attr2, opr2, t1_filter, t2_filter):
    t1_rows = data.filter(t1_filter)
    t2_rows = data.filter(t2_filter).sort_by(attr1)
    
    for row1 in t1_rows:
        # 1. Narrow down t2 rows using the first order predicate (A > A)
        candidates = t2_rows.search_range(row1[attr1], opr1)
        
        # 2. Further filter candidates using the second order predicate (B > B)
        # In code, this is optimized by using the sorted property of candidates
        violators = candidates.filter(attr2, opr2, row1[attr2])
        
        if violators:
            report_multi_cluster_conflict(row1.id, violators)
```

### E. DuckDBEngine
**Logic**: General fallback using SQL. Optimized for equality joins and handles NULLs correctly.

```python
def find_violations_general(data, dc):
    # 1. Translate DC predicates to SQL WHERE and JOIN clauses
    # Equality predicates (t1.A = t2.A) become JOIN ... ON ... IS NOT DISTINCT FROM
    # Unary and other binary predicates become WHERE clauses
    sql = translate_to_sql(dc) 
    
    # Example SQL:
    # SELECT t1._cid, t2._cid 
    # FROM clusters t1 JOIN clusters t2 ON t1.A IS NOT DISTINCT FROM t2.A
    # WHERE t1.B > t2.B AND t1.C != t2.D
    
    # 2. Execute query and collect violating pairs
    results = duckdb.query(sql)
    for cid1, cid2 in results:
        report_conflict(cid1, cid2)
```
