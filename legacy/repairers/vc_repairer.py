from dataclasses import dataclass

import igraph as ig
import numpy as np

from src.data_repair.data_repairer import DataRepairer
from src.data_repair.vertex_cover.weight_function import VertexWeightFunction
from src.entities.dataset import Dataset
from src.entities.marginal import Marginal


@dataclass(slots=True)
class VCRepairer(DataRepairer):
    weight_function: VertexWeightFunction

    def repair(
        self,
        synthetic_data: Dataset,
        marginals: list[Marginal],
    ) -> Dataset:
        edges = synthetic_data.violating_pairs()
        graph = ig.Graph(n=len(synthetic_data.data), edges=edges, directed=False)
        graph.vs["source_idx"] = list(range(len(synthetic_data.data)))
        removed = self._min_weight_cover(graph, synthetic_data, marginals)
        repaired_data = synthetic_data.data.drop(index=list(removed)).reset_index(
            drop=True
        )
        return Dataset(
            name="repaired_vc",
            data=repaired_data,
            denial_constraints=list(synthetic_data.denial_constraints),
            metadata=dict(synthetic_data.metadata),
        )

    def _min_weight_cover(
        self, graph: ig.Graph, dataset: Dataset, marginals: list[Marginal]
    ) -> set[int]:
        cover: set[int] = set()
        base_weights = self.weight_function.compute(dataset.data, marginals)
        while graph.ecount() > 0:
            source_indices = graph.vs["source_idx"]
            local_weights = np.array(
                [base_weights[idx] for idx in source_indices], dtype=float
            )
            local_degrees = np.array(graph.degree(), dtype=float)
            score = self._normalize(local_weights) / np.maximum(
                self._normalize(local_degrees), 1e-9
            )
            chosen_local = int(np.argmin(score))
            chosen_source = int(source_indices[chosen_local])
            cover.add(chosen_source)
            to_remove = [chosen_local] + [v.index for v in graph.vs if v.degree() == 0]
            graph.delete_vertices(sorted(set(to_remove), reverse=True))
        return cover

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        low = float(values.min(initial=0.0))
        high = float(values.max(initial=0.0))
        if abs(high - low) < 1e-9:
            return np.ones_like(values)
        return (values - low) / (high - low)
