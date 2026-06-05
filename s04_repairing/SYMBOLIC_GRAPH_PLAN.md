# Symbolic Conflict Graph Implementation Plan

## Goal
Resolve memory overflow in `s04_repairing` during Vertex Cover (VC) repair for highly violated datasets. The current implementation materializes an explicit $O(N^2)$ edge list via `np.meshgrid` in `ViolationFinder` and `igraph.Graph.add_edges`, causing immediate Out-of-Memory (OOM) errors on large graphs.

## Strategy: Biclique Compression
Instead of storing individual edges, we represent conflicts as **Bicliques** (Complete Bipartite Graphs). If a set of tuples $A$ violates a constraint against a set of tuples $B$, we store the tuple $(A, B)$ rather than $|A| \times |B|$ edges.

This requires two major changes:
1.  **Upstream Prevention (`ViolationFinder`)**: Stop generating $O(N^2)$ DataFrames. Return a list of `(List[int], List[int])` pairs.
2.  **Downstream Processing (`SymbolicConflictGraph`)**: Create a virtual graph class that provides the API expected by the repairers (`degree`, `ecount`, `delete_vertex`) without ever instantiating the full edge list.

## Implementation Steps

### Phase 1: The `BicliqueCollection`
Create a data structure to hold the compressed violations.
*   **File**: `shared/entities/violations.py` (or similar).
*   **Structure**: A list of groups. Each group is a dictionary or dataclass containing two sets of indices: `left_nodes` and `right_nodes`.

### Phase 2: Refactor `ViolationFinder`
Modify the engines to return the `BicliqueCollection`.
*   **Pandas Engine (FDs & Constants)**: Instead of `np.meshgrid`, simply append `(idx1, idx2)` arrays to the collection.
*   **SQL Engine (Order Constraints)**: This requires slightly more work. We can use DuckDB to find range boundaries (e.g., "Row $i$ conflicts with rows $j$ to $K$") and store these as `([i], range(j, K+1))`.

### Phase 3: The `SymbolicConflictGraph`
Implement a lightweight graph replacement in `s04_repairing`.
*   **File**: `s04_repairing/src/repair/symbolic_graph.py`.
*   **API Requirements**: Must duck-type enough of `igraph.Graph` to satisfy `VertexCoverRepairer` and `WeightedVCRepairer`.
    *   `.vs` (Vertex sequence simulation)
    *   `.degree(indices)`
    *   `.ecount()`
    *   `.delete_edges()` (which we will map to a custom `delete_vertex` logic)

### Phase 4: Integration and Parity Testing
*   Update `Dataset.get_violations()` to return the new structure.
*   Update `VertexCoverRepairer._build_conflict_graph` to instantiate `SymbolicConflictGraph`.
*   **Crucial Test**: Run existing tests in `s04_repairing/tests` to guarantee bit-for-bit parity with the legacy `igraph` implementation on small datasets.

## Risk Mitigation
*   **Overlapping Bicliques**: If a row is in multiple bicliques that share the same opposing node, the naive degree sum would double-count the edge. The `SymbolicConflictGraph` must handle degree calculation using sets or lazy evaluation to maintain exact parity with `igraph.simplify()`.
*   **Too Many Bicliques**: For complex SQL inequalities, the number of bicliques might approach $O(N)$. However, this is still strictly better than $O(N^2)$ edges.
