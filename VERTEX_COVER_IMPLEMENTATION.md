# Technical Specification: Vertex Cover Repair Framework

This document provides a detailed blueprint for re-implementing the Vertex Cover (VC) based repair system. It covers the core logic, the utility-aware weighting, and the critical optimizations required to avoid $O(N^2)$ memory bottlenecks.

---

## 1. Problem Definition
**Goal:** Given a dataset $D$ with $N$ rows and a set of Denial Constraints $\Sigma$, remove the minimum number of rows (or the "least valuable" rows) such that no two remaining rows violate any constraint in $\Sigma$.

**Graph Mapping:**
- **Vertices ($V$):** Each row in the dataset is a vertex.
- **Edges ($E$):** An edge exists between $v_i$ and $v_j$ if the pair $(t_i, t_j)$ violates a denial constraint.
- **Objective:** Find a **Vertex Cover** $VC \subseteq V$ such that for every edge $(u, v) \in E$, at least one endpoint is in $VC$.

---

## 2. Core Algorithm: Greedy Weighted VC
The framework uses an iterative greedy approach. Instead of finding the optimal solution (which is NP-Hard), we use a heuristic that scales.

### The Selection Formula
In every iteration, we calculate a score for every "active" vertex (vertex with degree > 0) and remove the one with the lowest score:

$$Score(v) = (1 - \alpha) \cdot \text{UtilityWeight}(v) + \alpha \cdot (1 - \text{NormDegree}(v))$$

- **$\text{NormDegree}(v)$:** The number of current violations $v$ is involved in, normalized to $[0, 1]$.
- **$\text{UtilityWeight}(v)$:** How much removing $v$ hurts the statistical distribution (marginals).
- **$\alpha$ (Alpha):** A hyper-parameter $(0 \dots 1)$. 
    - $\alpha \to 1$: Pure Greedy (removes max degree, ignores utility).
    - $\alpha \to 0$: Pure Utility (preserves data, might remove many rows).

---

## 3. Re-Implementation Guide (Step-by-Step)

### Step 1: Violation Identification
Do not generate a list of all pairs. Use a **Biclique Finder**. 
- If a set of rows $L$ conflicts with a set of rows $R$ on the same constraint values, store them as a **Biclique** $(L, R)$.
- **Memory Check:** Storing edges for $1000 \times 1000$ conflicts takes $1,000,000$ integers. Storing a Biclique takes $2,000$.

### Step 2: The Main Loop
1. **Initialize Graph:** Load bicliques into a "Symbolic Graph" (see Optimizations).
2. **Initialize Utility:** Pre-calculate the current counts of all marginal buckets.
3. **While $E > 0$:**
    a. Calculate $Score(v)$ for all $v$ where $Degree(v) > 0$.
    b. $v^* = \text{argmin}(Score)$.
    c. Add $v^*$ to `RemovedSet`.
    d. **Update Graph:** Decrease the degree of all neighbors of $v^*$.
    e. **Update Utility:** Decrement counts for all marginal buckets that $v^*$ belonged to.
4. **Result:** Return the dataset excluding `RemovedSet`.

---

## 4. Critical Optimizations (The "Secret Sauce")

### Optimization A: The Symbolic Conflict Graph
**Problem:** In large datasets, the number of edges can exceed 100 Billion, crashing memory.
**Solution:** Never materialize edges. Use a symbolic representation:
- Maintain an array `Degrees` of size $N$.
- For each Biclique $(L, R)$:
    - Initial `Degrees[L] += len(R)`
    - Initial `Degrees[R] += len(L)`
- **When $v \in L$ is deleted:**
    - Iterate through all Bicliques where $v \in L$.
    - `Degrees[R] -= 1` (This is a vectorized operation: `degrees[biclique.R] -= 1`).
    - This allows $O(N)$ memory and $O(1)$ edge deletion.

### Optimization B: Vectorized Utility (Matching Matrix)
**Problem:** Re-calculating marginal utility for every row in every iteration is $O(N \cdot M)$.
**Solution:** 
1. Create a sparse boolean matrix $M$ of size $N \times (\text{Number of Marginal Buckets})$.
2. $M_{i,j} = 1$ if row $i$ falls into marginal bucket $j$.
3. Pre-calculate the "Gain Vector" $G$: $G_j = \text{Impact on distance if bucket } j \text{ loses 1 count}$.
4. **Weight Calculation:** The utility weight for all rows is the matrix-vector product $W = M \times G$.

### Optimization C: Group-Aware Repair
**Problem:** Many rows are identical in categorical data.
**Solution:**
- Group identical rows into a single vertex with a `weight = count`.
- The degree of a group vertex is its conflict count multiplied by the size of the conflicting groups.
- Removing one group vertex removes multiple rows at once, speeding up the loop by $10x-100x$.

---

## 5. Hyper-parameter: Adaptive Alpha
To make the algorithm "Idiot-Proof," use **Adaptive Alpha**. Instead of the user picking $\alpha$, calculate it based on the graph topology:

1. **Calculate Hubbiness:** $h = \text{std}(\text{Degrees}) / \text{mean}(\text{Degrees})$.
2. If $h$ is high (there are "hubs" causing many violations), set $\alpha$ high to kill the hubs quickly.
3. As the graph becomes "flatter" (violations are spread out), lower $\alpha$ to focus on preserving the remaining utility.

---

## 6. Implementation Checklist
- [ ] **Biclique Collection:** Are violations grouped into $(L, R)$ sets?
- [ ] **Vectorized Degrees:** Are you using NumPy to decrement degrees across arrays?
- [ ] **Matching Matrix:** Is the utility calculation a matrix multiplication?
- [ ] **Early Exit:** Does the loop stop exactly when `sum(Degrees) == 0`?
- [ ] **Alpha Normalization:** Are $Weight$ and $Degree$ both scaled to $[0, 1]$ before scoring? (Crucial for balanced selection).
