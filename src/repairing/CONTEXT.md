# Repairers 

## Goal
The repairing stage is responsible for resolving conflicts (violations of denial constraints) in the synthetic dataset while preserving statistical utility as defined by a set of marginals.

## Repairers 
1. **Repairer**: Abstract base class for all repair strategies.
2. **ILP**: Formulates the repair as an Integer Linear Programming problem to find the optimal set of tuples to remove to minimize a weighted loss of removal and marginal distance.
3. **Weighted Vertex Cover**: A heuristic approach that iteratively removes tuples based on a balance between their conflict degree and their contribution to marginal utility.
4. **Vanilla Vertex Cover**: A simplified greedy vertex cover that removes tuples with the highest conflict degree.
5. **Classic Vertex Cover**: Removes a random vertex from the conflict graph.

### ILP Formulation
The ILP formulation minimizes a weighted combination of tuple removal and marginal divergence:
$$
\begin{small}
\smallskip
\hrule
\revised{
\begin{align}\label{ilp:global}
    \textbf{Minimize }&\alpha \cdot \frac{n - \sum_{l=1}^{n} x_l}{n} \;+\; \frac{1-\alpha}{|\marginalset|}\sum_{m \in \marginalset} d_m \quad \textbf{subject to:}\\
    x_i + x_j &\leq 1, \qquad \text{for all $t_i,t_j$ conflicting on a constraint in } \constraints \nonumber\\
    d_m \cdot \sum_{l}x_l &\geq \!\!\sum_{l:\, t_l[A_i]=a_1,\, t_l[A_j]=a_2}\!\!\!x_l \;-\; \tmarg{D_p}{a_1}{a_2} \cdot \sum_{l}x_l, \quad \forall\; m=(A_i{=}a_1, A_j{=}a_2) \in \marginalset \nonumber\\
    d_m \cdot \sum_{l} x_l &\geq \tmarg{D_p}{a_1}{a_2} \codt \sum_{l} x_l\;-\; \!\!\sum_{l:\, t_l[A_i]=a_1,\, t_l[A_j]=a_2}\!\!\!x_l, \quad \forall\; m \in \marginalset \nonumber\\
    d_m &\geq 0, \quad \forall\; m \in \marginalset \nonumber\\
    x_l &\in \{0,1\}, \quad \forall\; l \in [1,n] \nonumber
\end{align}}
\hrule
\smallskip
\end{small}
$$

### Weighted Vertex Cover Logic
1. Build conflict graph for the data.
2. Iteratively select vertices to remove:
   - Calculate weight $w(v_t)$ as the distance between hypothetical marginals (after removing $v_t$) and target marginals: $w_i(v_t) = \frac{1-\alpha}{|\marginalset|} \sum_{m \in \marginalset} |m_{D^{(v_t)}}-m|$.
   - Normalize weights and degrees.
   - Select vertex with minimal ratio `weight/degree`.
   - Update internal counts and remove incident edges.
3. Remove the selected vertices from the dataset.

## Testing
The repairing system is verified by tests in `tests/repairing/`.

### 1. Vertex Cover Repairer Tests (`test_vc_repairers.py`)
Validates the heuristic repair strategies:
- **`VanillaVCRepairer`**: Ensures it correctly identifies and resolves conflicts in a small dataset by removing minimum tuples based on degree.
- **`WeightedVCRepairer`**: Verifies that the repairer respects the utility weights. Tests confirm that the repairer correctly calculates the hypothetical distance to target marginals for each vertex and prefers removing tuples that minimize this distance.
- **State Management**: Ensures that internal caches (counts, tuple matches) are correctly initialized and updated during the iterative process.

### 2. ILP Repairer Tests (`test_ilp_repairer.py`)
Validates the optimal repair strategy:
- **Optimization Logic**: Confirms that Gurobi correctly solves the formulated ILP to resolve all violations while minimizing the defined loss function.
- **Marginal Preservation**: Verifies that the ILP selects the optimal subset of tuples that best matches the target marginals when multiple conflict-resolution options exist.
- **Environment Handling**: Includes checks for Gurobi availability and licensing, skipping tests gracefully if the solver is unavailable.

