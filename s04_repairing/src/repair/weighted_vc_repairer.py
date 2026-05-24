from dataclasses import dataclass, field
from typing import List, Optional

import igraph as ig
import numpy as np

from s04_repairing.src.repair.adaptive_alpha_calculator import AdaptiveAlphaCalculator
from s04_repairing.src.repair.vertex_cover_repairer import VertexCoverRepairer
from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet


@dataclass
class WeightedVCRepairer(VertexCoverRepairer):
    """
    Highly optimized Weighted Vertex Cover repair.
    """

    alpha: float
    use_adaptive_alpha: bool = False

    _alpha_calculator: Optional[AdaptiveAlphaCalculator] = field(
        init=False, default=None
    )
    _tuple_matches: List[np.ndarray] = field(init=False, default_factory=list)
    _current_counts: Optional[np.ndarray] = field(init=False, default=None)
    _current_n: int = field(init=False, default=0)
    _target_freqs: Optional[np.ndarray] = field(init=False, default=None)

    def _select_vertex(
        self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet
    ) -> int:
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

        # Capture optional fields into local variables for type narrowing
        current_counts = self._current_counts
        target_freqs = self._target_freqs

        if current_counts is None or target_freqs is None:
            return np.zeros(len(active_indices))

        if self._current_n <= 1:
            return self._handle_small_n(active_indices, m_len, target_freqs)

        diff_gain, base_sum = self._compute_base_metrics(
            m_len, current_counts, target_freqs
        )
        return self._compute_vertex_weights(active_indices, base_sum, diff_gain, m_len)

    def _handle_small_n(
        self, active_indices: list, m_len: int, target_freqs: np.ndarray
    ) -> np.ndarray:
        val = 1 / m_len * np.abs(target_freqs).sum()
        return np.full(len(active_indices), val)

    def _compute_base_metrics(
        self, m_len: int, current_counts: np.ndarray, target_freqs: np.ndarray
    ):
        N_prime = self._current_n - 1
        base_diffs = np.abs(current_counts / N_prime - target_freqs)
        hypo_diffs = np.abs((current_counts - 1) / N_prime - target_freqs)
        return hypo_diffs - base_diffs, base_diffs.sum()

    def _compute_vertex_weights(
        self,
        active_indices: List[int],
        base_sum: float,
        diff_gain: np.ndarray,
        m_len: int,
    ) -> np.ndarray:
        weights: List[float] = []
        for v_idx in active_indices:
            matches: np.ndarray = self._tuple_matches[v_idx]
            gain = float(diff_gain[matches].sum()) if matches.size > 0 else 0.0
            weights.append((base_sum + gain) / m_len)
        return np.array(weights)

    def _pick_best_vertex(
        self,
        active_indices: List[int],
        weights: np.ndarray,
        graph: ig.Graph,
        alpha: float,
    ) -> int:
        degrees = np.array([graph.degree(v_idx) for v_idx in active_indices])
        nw = self._normalize(weights)
        nd = -self._normalize(degrees)
        ratios = (1 - alpha) * nw + alpha * nd
        return int(active_indices[int(np.argmin(ratios))])

    def _update_state(self, chosen_v: int):
        matches = self._tuple_matches[chosen_v]
        current_counts = self._current_counts
        if matches.size > 0 and current_counts is not None:
            current_counts[matches] -= 1
        self._current_n -= 1

    def _precompute_initial_state(self, dataset: Dataset, marginals: MarginalSet):
        n = len(dataset.data)
        self._current_n = n
        current_counts = np.zeros(len(marginals))
        self._target_freqs = np.array([m.target for m in marginals])

        # Use local list for construction to avoid type mismatch with field hint
        tuple_matches_list: List[List[int]] = [[] for _ in range(n)]

        self._fill_initial_counts(
            dataset, marginals, current_counts, tuple_matches_list
        )

        self._current_counts = current_counts
        self._tuple_matches = [np.array(m, dtype=int) for m in tuple_matches_list]

    def _fill_initial_counts(
        self,
        dataset: Dataset,
        marginals: MarginalSet,
        current_counts: np.ndarray,
        tuple_matches_list: List[List[int]],
    ):
        for i, m in enumerate(marginals):
            mask = m.get_mask(dataset.data)
            matching_indices = np.where(mask)[0]
            current_counts[i] = len(matching_indices)
            for idx in matching_indices:
                tuple_matches_list[idx].append(i)

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        self._tuple_matches = []
        self._current_counts = None
        self._current_n = 0
        return super().repair(dataset, marginals)
