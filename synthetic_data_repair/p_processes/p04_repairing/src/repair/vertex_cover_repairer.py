from abc import abstractmethod
from typing import Any

import igraph as ig
import numpy as np

from s04_repairing.src.repair.repairer import Repairer
from u_utilities.u_shared.dataset import Dataset
from u_utilities.u_shared.marginal import MarginalSet


class VertexCoverRepairer(Repairer):
    """
    Base class for Vertex Cover based repair algorithms.
    """

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        graph = self._build_conflict_graph(dataset)
        removed_indices = self._find_vertex_cover(graph, dataset, marginals)

        keep_indices = [i for i in range(len(dataset.data)) if i not in removed_indices]
        data = dataset.data.iloc[keep_indices].reset_index(drop=True)

        return Dataset(
            name=f"{dataset.name}_repaired",
            data=data,
            dcs=dataset.dcs,
            target=dataset.target,
        )

    def _find_vertex_cover(self, graph, dataset, marginals) -> set:
        removed = set()
        while graph.ecount() > 0:
            selected = self._select_vertex(graph, dataset, marginals)
            v_indices = (
                [selected] if isinstance(selected, (int, np.integer)) else selected
            )
            for v_idx in v_indices:
                removed.add(int(v_idx))
                graph.delete_edges(graph.incident(v_idx))
        return removed

    def _build_conflict_graph(self, dataset: Dataset) -> Any:
        from s04_repairing.src.repair.symbolic_graph import SymbolicConflictGraph
        n = len(dataset.data)
        violations = dataset.get_violations()
        graph = SymbolicConflictGraph(n, violations)
        return graph

    @abstractmethod
    def _select_vertex(
        self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet
    ) -> Any:
        pass

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        min_val = np.min(values)
        max_val = np.max(values)
        return (values - min_val + 1e-8) / (max_val - min_val + 1e-8)
