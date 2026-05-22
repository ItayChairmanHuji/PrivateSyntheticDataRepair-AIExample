import numpy as np
import igraph as ig
from abc import abstractmethod
from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s04_repairing.src.repair.repairer import Repairer

class VertexCoverRepairer(Repairer):
    """
    Base class for Vertex Cover based repair algorithms.
    """
    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        graph = self._build_conflict_graph(dataset)
        removed_indices = self._find_vertex_cover(graph, dataset, marginals)
        
        keep_indices = [i for i in range(len(dataset.data)) if i not in removed_indices]
        data = dataset.data.iloc[keep_indices].reset_index(drop=True)
        
        return Dataset(name=f"{dataset.name}_repaired", data=data, dcs=dataset.dcs, target=dataset.target)

    def _find_vertex_cover(self, graph, dataset, marginals) -> set:
        removed = set()
        while graph.ecount() > 0:
            selected = self._select_vertex(graph, dataset, marginals)
            v_indices = [selected] if isinstance(selected, (int, np.integer)) else selected
            for v_idx in v_indices:
                removed.add(int(v_idx))
                graph.delete_edges(graph.incident(v_idx))
        return removed

    def _build_conflict_graph(self, dataset: Dataset) -> ig.Graph:
        n = len(dataset.data)
        graph = ig.Graph(n)
        graph.vs["original_index"] = list(range(n))
        violations = dataset.get_violations()
        if not violations.empty:
            graph.add_edges(violations[['idx1', 'idx2']].values.astype(int))
            graph.simplify()
        return graph

    @abstractmethod
    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> int:
        pass

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        if len(values) == 0:
            return values
        v_min, v_max = values.min(), values.max()
        return (values - v_min) / (v_max - v_min) if v_max != v_min else np.zeros_like(values)
