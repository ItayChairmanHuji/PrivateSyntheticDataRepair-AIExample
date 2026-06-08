from dataclasses import dataclass
import numpy as np
from p_processes.p04_repairing.src.core import ConflictGraphBuilder, Repairer
from u_utilities.u_shared import Dataset, MarginalSet
from .weights.base import WeightCalculator
from .alpha.base import AlphaCalculator

@dataclass
class WeightedVCRepairer(Repairer):
    weight_calculator: WeightCalculator
    alpha_calculator: AlphaCalculator

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        graph = ConflictGraphBuilder.build(len(dataset.data), dataset.get_violations())
        removed = set()

        while graph.has_edges():
            active = np.where(graph.active)[0]
            weights = self._normalize(self.weight_calculator.calculate_weights(graph, active))
            degrees = self._normalize(graph.degree(active))
            
            alpha = self.alpha_calculator.calculate_alpha(graph, active, degrees, weights)
            selected = int(active[np.argmin((1 - alpha) * weights - alpha * degrees)])

            removed.add(selected)
            graph.remove_vertex(selected)
            self.weight_calculator.update(selected)

        return self._create_output_dataset(dataset, removed)

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        min_v, max_v = np.min(values), np.max(values)
        return (values - min_v + 1e-8) / (max_v - min_v + 1e-8)

    def _create_output_dataset(self, dataset: Dataset, removed: set) -> Dataset:
        keep = [i for i in range(len(dataset.data)) if i not in removed]
        return Dataset(
            name=f"{dataset.name}_repaired",
            data=dataset.data.iloc[keep].reset_index(drop=True),
            dcs=dataset.dcs,
            target=dataset.target,
        )
