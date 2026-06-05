# Implementation Guide: Violation Finding for Denial Constraints (DCs)

This document provides a comprehensive, step-by-step blueprint for implementing an efficient violation-finding algorithm for Denial Constraints (DCs). It is designed to be "idiot-proof," guiding a developer from the mathematical definition to a high-performance, optimized implementation.

---

## 1. Problem Definition

A **Denial Constraint (DC)** is a rule that specifies what **cannot** happen in a dataset. 
Mathematically, it is expressed as:
$$\forall t_i, t_j \in D: \neg (P_1 \wedge P_2 \wedge \dots \wedge P_k)$$

A **violation** occurs when there exists a pair of tuples $(t_1, t_2)$ such that **all** predicates $P_1, \dots, P_k$ are **TRUE** simultaneously.

### The Goal
Given a dataset $D$ and a set of DCs $\Sigma$, find all pairs $(i, j)$ (indices of tuples) that violate any DC in $\Sigma$ and store them in a **Conflict Graph**.

---

## 2. Input Requirements

1.  **Dataset ($D$):** A table with $N$ rows and $M$ columns.
2.  **Constraints ($\Sigma$):** A list of DCs. Each DC is a list of predicates.
3.  **Predicate Structure:** Each predicate $P$ consists of:
    *   **Attribute:** The column it applies to (e.g., `Age`).
    *   **Operator:** The comparison operator (e.g., `==`, `!=`, `<`, `>`, `<=`, `>=`).
    *   **Scope:** Whether it compares $t_1$ to $t_2$ on the same attribute (`t1.A op t2.A`) or different attributes (`t1.A op t2.B`). Usually, DCs focus on the same attribute across tuples.

---

## 3. The Naive Algorithm ($O(N^2)$)

The simplest way to find violations is a double loop. 

**Logic:**
```python
violations = []
for i in range(len(D)):
    for j in range(len(D)):
        if i == j: continue # Skip self-comparison unless DC allows it
        
        # Check every DC
        for dc in Σ:
            all_predicates_satisfied = True
            for predicate in dc:
                if not predicate.evaluate(D[i], D[j]):
                    all_predicates_satisfied = False
                    break
            
            if all_predicates_satisfied:
                violations.append((i, j))
```

**Why this fails:** If you have 1,000,000 rows, $N^2$ is 1 trillion comparisons. This is the **"Quadratic Trap."**

---

## 4. The Optimized Algorithm (The "Pruned Search")

To scale, we must avoid comparing tuples that have no chance of violating the DC. We use **indexing** and **sorting** to prune the search space.

### Optimization A: The "Equality Pivot" (For == Predicates)
If a DC contains an equality predicate (e.g., `t1.ZipCode == t2.ZipCode`), we only need to compare tuples that share the same `ZipCode`.

1.  **Group** tuples by the value of the equality attribute (using a Hash Map/Dictionary).
2.  **Iterate** only within each group.
3.  **Result:** Reduces complexity from $O(N^2)$ to $O(\sum |group|^2)$, which is often near-linear for high-cardinality columns.

### Optimization B: Sort-Based Windowing (For Inequality Predicates)
If a DC contains a range predicate (e.g., `t1.Salary < t2.Salary`), we can sort the data.

1.  **Sort** the dataset by `Salary`.
2.  **Use a Sliding Window:** For a tuple $t_i$, only look at tuples $t_j$ that satisfy the inequality. 
3.  **Note:** This is dangerous if the range is wide (e.g., "Salary is different"), as it reverts to $O(N^2)$.

### Optimization C: Predicate Ordering
Evaluate the most selective predicates first.
*   `==` (Equality) is highly selective.
*   `<` or `>` are moderately selective.
*   `!=` (Not Equal) is **not** selective (it matches almost everything). **Always evaluate `!=` last.**

### Optimization D: Biclique Compression (Advanced)
A **Biclique** $(L, R)$ is a compact way to represent a large number of violation edges. If every tuple in set $L$ violates the DC with every tuple in set $R$, we store the two sets rather than $|L| \times |R|$ individual edges.

1.  **Group identical tuples:** Many rows might have identical values for all attributes mentioned in the DC. Group these into a single "meta-node."
2.  **Compare Meta-Nodes:** If Meta-Node $A$ and Meta-Node $B$ violate a DC, it implies a biclique between all rows in $A$ and all rows in $B$.
3.  **Result:** This can reduce a 1-billion-edge graph into a few thousand bicliques, saving gigabytes of RAM.

### Optimization E: Symmetry and Self-Violations
*   **Symmetry:** A DC check for $(t_1, t_2)$ often yields the same result as $(t_2, t_1)$. To avoid redundant work, you can iterate $j > i$. However, if your DC contains asymmetric operators like `<` or `>`, you must check both directions **OR** normalize the DC.
*   **Self-Violations:** A single tuple $t_i$ can violate a DC if $P(t_i, t_i)$ is true. While rare in standard integrity rules, your algorithm should explicitly decide whether to check $i=j$ based on the DC's logic.

---

## 5. Implementation Blueprint (The "Elite" Version)

### Step 1: Pre-Processing (Grouping)
Group the dataset by **all** attributes involved in the DC.
```python
relevant_attrs = [p.attribute for p in dc]
groups = dataset.groupby(relevant_attrs).indices 
# groups is { (val1, val2, ...): [row_idx1, row_idx2, ...] }
```

### Step 2: Partitioning
If the DC has an equality predicate (e.g., `t1.Zip == t2.Zip`), further partition these groups. Only groups with the same `Zip` can violate each other.

### Step 3: Vectorized Group Comparison
```python
def check_groups(group_values, dc):
    # group_values is a matrix where each row represents a unique combination of attributes
    # Use NumPy broadcasting to compare all pairs of unique values
    v1 = group_values[:, None, :]
    v2 = group_values[None, :, :]
    
    # Evaluate all predicates at once
    mask = np.ones((len(group_values), len(group_values)), dtype=bool)
    for pred in dc:
        mask &= evaluate_vectorized(v1, v2, pred)
        
    # mask[i, j] == True means Group i and Group j violate the DC
    return np.argwhere(mask)
```

---

## 6. Critical Performance Warnings

1.  **The Range Explosion:** If you have a DC like `t1.Income < t2.Income` and your data is sorted, almost half the pairs might violate it. If $N=100,000$, the number of edges could be $5,000,000,000$. This will crash your memory.
    *   **Fix:** Use **Sparse Representation** for the conflict graph.
    *   **Fix:** If the number of violations exceeds a threshold (e.g., $10^7$), stop and warn the user.
2.  **Symmetry:** If $(i, j)$ is a violation, $(j, i)$ is often also a violation. Don't store both unless your algorithm specifically requires a directed graph. Storing only $i < j$ halves memory usage.
3.  **Memory Management:** For very large datasets, use `bitsets` to track which tuples are involved in at least one violation before building the full graph.

---

## 7. Idiot-Proof Checklist for Verification

*   [ ] Does your algorithm find the same number of violations as the $O(N^2)$ version on a small (100 row) sample?
*   [ ] Did you handle `NULL` values? (Usually, `NULL == NULL` is false in DC logic).
*   [ ] Is your conflict graph index-based (storing row numbers) rather than object-based?
*   [ ] If you have multiple DCs, do you merge the violations into a single graph? (Nodes = Rows, Edge = Violation of *any* DC).

---

## 8. Summary Table of Complexity

| Strategy | Complexity | Best For... |
| :--- | :--- | :--- |
| **Naive NLJ** | $O(N^2)$ | Testing/Small data (< 1000 rows) |
| **Hash Grouping** | $O(N \cdot |Group|)$ | DCs with at least one `==` predicate |
| **Sort-Based** | $O(N \log N)$ | DCs with `<` or `>` but no `==` |
| **Vectorized** | $O(N^2)$ (fast constant) | Small groups with complex predicates |
