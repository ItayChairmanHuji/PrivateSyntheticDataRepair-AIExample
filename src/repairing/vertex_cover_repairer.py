import numpy as np
import igraph as ig
from abc import abstractmethod
from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet
from src.repairing.repairer import Repairer

class VertexCoverRepairer(Repairer):
    """
    Base class for Vertex Cover based repair algorithms.
    Optimized to use edge-deletion to keep vertex indices stable.
    """
    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        # 1. Build conflict graph
        graph = self._build_conflict_graph(dataset)
        
        # 2. Iteratively select vertices to "cover" edges
        removed_indices = set()
        
        while graph.ecount() > 0:
            # select_vertex can return a single index or a list of indices
            selected = self._select_vertex(graph, dataset, marginals)
            
            if isinstance(selected, (int, np.integer)):
                v_indices = [selected]
            else:
                v_indices = selected
            
            for v_idx in v_indices:
                removed_indices.add(int(v_idx))
                # Deleting incident edges makes the vertex "isolated" (degree 0).
                incident_edges = graph.incident(v_idx)
                graph.delete_edges(incident_edges)
        
        # 3. Drop the tuples in the cover from the data
        keep_indices = [i for i in range(len(dataset.data)) if i not in removed_indices]
        repaired_data = dataset.data.iloc[keep_indices].reset_index(drop=True)
        
        return Dataset(
            name=f"{dataset.name}_repaired",
            data=repaired_data,
            dcs=dataset.dcs,
            target=dataset.target
        )

    def _build_conflict_graph(self, dataset: Dataset) -> ig.Graph:
        n = len(dataset.data)
        graph = ig.Graph(n)
        graph.vs["original_index"] = list(range(n))
        
        violations = dataset.get_violations()
        
        if not violations.empty:
            edges = list(zip(violations['idx1'].astype(int), violations['idx2'].astype(int)))
            graph.add_edges(edges)
            graph.simplify()
            
        return graph

    @abstractmethod
    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> int:
        pass

    def _normalize(self, values: np.ndarray, eps=1e-9) -> np.ndarray:
        if len(values) == 0:
            return values
        v_min = values.min()
        v_max = values.max()
        if v_max == v_min:
            return np.ones_like(values)
        return (values - v_min + eps) / (v_max - v_min + eps)
