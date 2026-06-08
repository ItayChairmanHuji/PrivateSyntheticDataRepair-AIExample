from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from p_processes.p04_repairing.src.core import Graph, Repairer
from u_utilities.u_shared import Dataset, MarginalSet

from .adaptive_alpha_calculator import AdaptiveAlphaCalculator


@dataclass
class WeightedVCRepairer(Repairer):
    alpha: float
    use_adaptive_alpha: bool = True
    use_auto_alpha: bool = False

    _auto_alpha: Optional[float] = field(init=False, default=None)
    _alpha_calculator: Optional[AdaptiveAlphaCalculator] = field(init=False, default=None)
    _matching_matrix: Optional[np.ndarray] = field(init=False, default=None)
    _current_counts: Optional[np.ndarray] = field(init=False, default=None)
    _current_n: int = field(init=False, default=0)

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        self._init_state(dataset, marginals)
        violations = dataset.get_violations()
        n_rows = len(dataset.data)

        graph = Graph(n_rows, violations)

        if self.use_auto_alpha:
            self._auto_alpha = self._calculate_auto_alpha(graph)
        elif self.use_adaptive_alpha:
            self._alpha_calculator = AdaptiveAlphaCalculator()

        removed = set()
        while graph.ecount() > 0:
            active_indices = graph.vs.select(_degree_gt=0)

            # 1. Calculate Weights
            weights = self._calculate_weights(active_indices, len(marginals))
            degrees = graph.degree(active_indices)

            norm_weights = self._normalize(weights)
            norm_degrees = self._normalize(degrees)

            # 2. Get Alpha
            alpha = self._get_alpha(graph, active_indices, norm_degrees, norm_weights)

            # 3. Pick Vertex
            ratios = (1 - alpha) * norm_weights - alpha * norm_degrees
            selected = int(active_indices[int(np.argmin(ratios))])

            # 4. Update
            removed.add(selected)
            graph.delete_edges(selected)
            self._update_state(selected)

        keep_indices = [i for i in range(n_rows) if i not in removed]
        data = dataset.data.iloc[keep_indices].reset_index(drop=True)

        return Dataset(
            name=f"{dataset.name}_repaired",
            data=data,
            dcs=dataset.dcs,
            target=dataset.target,
        )

    def _init_state(self, dataset: Dataset, marginals: MarginalSet):
        n = len(dataset.data)
        self._current_n = n
        m_len = len(marginals)
        self._current_counts = np.zeros(m_len)
        self._target_freqs = np.array([m.target for m in marginals])
        self._matching_matrix = np.zeros((n, m_len), dtype=bool)
        for i, m in enumerate(marginals):
            mask = m.get_mask(dataset.data)
            self._matching_matrix[:, i] = mask
            self._current_counts[i] = np.sum(mask)

    def _calculate_auto_alpha(self, graph) -> float:
        degrees = np.array(graph.degree())
        mean_deg = np.mean(degrees)
        if mean_deg == 0:
            return 0.0
        cv = np.std(degrees) / mean_deg
        return float(cv / (cv + 1))

    def _get_alpha(self, graph, active_indices, norm_degrees, norm_weights) -> float:
        if self.use_auto_alpha and self._auto_alpha is not None:
            return self._auto_alpha
        if self.use_adaptive_alpha and self._alpha_calculator:
            alpha, _, _ = self._alpha_calculator.calculate_alpha(graph, active_indices, norm_degrees, norm_weights)
            return alpha
        return self.alpha

    def _calculate_weights(self, active_indices, m_len) -> np.ndarray:
        if m_len == 0 or self._current_n <= 1:
            return np.zeros(len(active_indices))

        N_prime = self._current_n - 1
        base_diffs = np.abs(self._current_counts / N_prime - self._target_freqs)
        hypo_diffs = np.abs((self._current_counts - 1) / N_prime - self._target_freqs)
        diff_gain = hypo_diffs - base_diffs

        active_matrix = self._matching_matrix[active_indices]
        gain = active_matrix @ diff_gain
        return (base_diffs.sum() + gain) / m_len

    def _update_state(self, chosen_v: int):
        matches = np.where(self._matching_matrix[chosen_v])[0]
        if matches.size > 0:
            self._current_counts[matches] -= 1
        self._current_n -= 1

    def _normalize(self, values: np.ndarray) -> np.ndarray:
        min_v, max_v = np.min(values), np.max(values)
        return (values - min_v + 1e-8) / (max_v - min_v + 1e-8)
