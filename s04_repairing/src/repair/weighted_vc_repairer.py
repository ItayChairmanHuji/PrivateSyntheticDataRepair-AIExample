from dataclasses import dataclass, field
from typing import Optional, List, Any

import igraph as ig
import numpy as np

from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s04_repairing.src.repair.vertex_cover_repairer import VertexCoverRepairer
from s04_repairing.src.repair.adaptive_alpha_calculator import AdaptiveAlphaCalculator

@dataclass
class WeightedVCRepairer(VertexCoverRepairer):
    """
    Highly optimized Weighted Vertex Cover repair.
    """
    alpha: float
    use_adaptive_alpha: bool = False
    
    _alpha_calculator: Optional[AdaptiveAlphaCalculator] = field(init=False, default=None)
    _tuple_matches: List[np.ndarray] = field(init=False, default_factory=list)
    _current_counts: Optional[np.ndarray] = field(init=False, default=None)
    _current_n: int = field(init=False, default=0)
    _target_freqs: Optional[np.ndarray] = field(init=False, default=None)

    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> int:
        if not self._tuple_matches:
            self._init_state(dataset, marginals)

        active_indices = [v.index for v in graph.vs.select(_degree_gt=0)]
        if not active_indices:
            return -1

        weights = self._calculate_weights(active_indices, len(marginals))
        alpha = self._get_alpha(graph, active_indices)
        
        chosen_v = self._pick_best_vertex(active_indices, weights, graph, alpha)
        self._update_state(chosen_v)
        return chosen_v

    def _init_state(self, dataset: Dataset, marginals: MarginalSet):
        self._precompute_initial_state(dataset, marginals)
        if self.use_adaptive_alpha:
            self._alpha_calculator = AdaptiveAlphaCalculator()

    def _get_alpha(self, graph: ig.Graph, active_indices: list) -> float:
        if self.use_adaptive_alpha and self._alpha_calculator:
            return self._alpha_calculator.calculate_alpha(graph, active_indices)
        return self.alpha

    def _calculate_weights(self, active_indices: list, m_len: int) -> np.ndarray:
        if m_len == 0:
            return np.zeros(len(active_indices))
        if self._current_n <= 1:
            return self._handle_small_n(active_indices, m_len)
        
        diff_gain, base_sum = self._compute_base_metrics(m_len)
        return self._compute_vertex_weights(active_indices, base_sum, diff_gain, m_len)

    def _handle_small_n(self, active_indices: list, m_len: int) -> np.ndarray:
        val = 1 / m_len * np.abs(self._target_freqs).sum() if self._target_freqs is not None else 0
        return np.full(len(active_indices), val)

    def _compute_base_metrics(self, m_len: int):
        N_prime = self._current_n - 1
        base_diffs = np.abs(self._current_counts / N_prime - self._target_freqs)
        hypo_diffs = np.abs((self._current_counts - 1) / N_prime - self._target_freqs)
        return hypo_diffs - base_diffs, base_diffs.sum()

    def _compute_vertex_weights(self, active_indices, base_sum, diff_gain, m_len):
        weights = []
        for v_idx in active_indices:
            matches = self._tuple_matches[v_idx]
            gain = diff_gain[matches].sum() if matches.size > 0 else 0
            weights.append((base_sum + gain) / m_len)
        return np.array(weights)

    def _pick_best_vertex(self, active_indices, weights, graph, alpha) -> int:
        degrees = np.array([graph.degree(v_idx) for v_idx in active_indices])
        nw = self._normalize(weights)
        nd = self._normalize(degrees)
        ratios = (1 - alpha) * nw + alpha * (1 - nd)
        return active_indices[np.argmin(ratios)]

    def _update_state(self, chosen_v: int):
        matches = self._tuple_matches[chosen_v]
        if matches.size > 0 and self._current_counts is not None:
            self._current_counts[matches] -= 1
        self._current_n -= 1

    def _precompute_initial_state(self, dataset: Dataset, marginals: MarginalSet):
        n = len(dataset.data)
        self._current_n = n
        self._current_counts = np.zeros(len(marginals))
        self._target_freqs = np.array([m.target for m in marginals])
        self._tuple_matches = [[] for _ in range(n)]
        self._fill_initial_counts(dataset, marginals)
        self._tuple_matches = [np.array(m, dtype=int) for m in self._tuple_matches]

    def _fill_initial_counts(self, dataset, marginals):
        for i, m in enumerate(marginals):
            mask = m.get_mask(dataset.data)
            matching_indices = np.where(mask)[0]
            self._current_counts[i] = len(matching_indices)
            for idx in matching_indices:
                self._tuple_matches[idx].append(i)

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        self._tuple_matches = []
        self._current_counts = None
        self._current_n = 0
        return super().repair(dataset, marginals)
