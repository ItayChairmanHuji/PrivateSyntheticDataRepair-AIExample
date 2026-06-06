from abc import abstractmethod
from typing import Any

import igraph as ig
import numpy as np

from .repairer import Repairer
from u_utilities.u_shared import Dataset
from u_utilities.u_shared import MarginalSet


class VertexCoverRepairer(Repairer):
    """
    Base class for Vertex Cover based repair algorithms.
    """

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        import time
        self.profiler = {
            "graph_status_ns": 0,
            "vertex_selection_ns": 0,
            "graph_deletion_ns": 0,
            "total_iterations": 0
        }
        
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
        import time
        removed = set()
        while True:
            t0 = time.perf_counter_ns()
            has_edges = graph.ecount() > 0
            self.profiler["graph_status_ns"] += time.perf_counter_ns() - t0
            
            if not has_edges:
                break
                
            t1 = time.perf_counter_ns()
            selected = self._select_vertex(graph, dataset, marginals)
            self.profiler["vertex_selection_ns"] += time.perf_counter_ns() - t1
            
            t2 = time.perf_counter_ns()
            v_indices = (
                [selected] if isinstance(selected, (int, np.integer)) else selected
            )
            for v_idx in v_indices:
                removed.add(int(v_idx))
                graph.delete_edges(v_idx)
            self.profiler["graph_deletion_ns"] += time.perf_counter_ns() - t2
            
            self.profiler["total_iterations"] += 1
            
        return removed

    def _build_conflict_graph(self, dataset: Dataset) -> Any:
        violations = dataset.get_violations()
        n_rows = len(dataset.data)
        
        # Group-Aware Optimization:
        # If violations are expressed as group conflicts, build a group-level graph.
        if violations.row_to_group is not None and violations.group_indices is not None:
            from .symbolic_graph import GroupAwareGraph
            return GroupAwareGraph(n_rows, violations)
        
        from .symbolic_graph import SymbolicConflictGraph
        return SymbolicConflictGraph(n_rows, violations)


    @abstractmethod
    def _select_vertex(
        self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet
    ) -> Any:
        pass

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        min_val = np.min(values)
        max_val = np.max(values)
        return (values - min_val + 1e-8) / (max_val - min_val + 1e-8)
