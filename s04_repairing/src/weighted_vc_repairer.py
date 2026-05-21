from dataclasses import dataclass, field
from typing import Optional

import igraph as ig
import numpy as np

from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s04_repairing.src.vertex_cover_repairer import VertexCoverRepairer
from s04_repairing.src.adaptive_alpha_calculator import AdaptiveAlphaCalculator


@dataclass
class WeightedVCRepairer(VertexCoverRepairer):
    """
    Highly optimized Weighted Vertex Cover repair.
    Uses iterative frequency updates to avoid scanning the dataset in each iteration.
    """

    alpha: float
    use_adaptive_alpha: bool = False
    _alpha_calculator: Optional[AdaptiveAlphaCalculator] = field(default=None, init=False)
    
    # Cache for matching marginals per tuple (Relation function rho)
    _tuple_matches: list = field(default_factory=list, init=False)
    # Current counts per marginal (Count vector c)
    _current_counts: np.ndarray = field(default=None, init=False)
    # Current total size of the data (n)
    _current_n: int = field(default=0, init=False)

    def _select_vertex(
        self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet
    ) -> int:
        if not self._tuple_matches:
            self._precompute_initial_state(dataset, marginals)
            if self.use_adaptive_alpha:
                self._alpha_calculator = AdaptiveAlphaCalculator()

        active_indices = self._get_active_indices(graph)
        if not active_indices:
            return -1

        weights = self._calculate_weights(active_indices, len(marginals))

        # Update alpha dynamically if enabled
        current_alpha = self.alpha
        if self.use_adaptive_alpha:
            current_alpha = self._alpha_calculator.calculate_alpha(graph, active_indices)

        chosen_v = self._pick_best_vertex(active_indices, weights, graph, current_alpha)
        self._update_state(chosen_v)

        return chosen_v

    def _get_active_indices(self, graph: ig.Graph) -> list:
        active_vs = graph.vs.select(_degree_gt=0)
        return [v.index for v in active_vs]

    def _calculate_weights(self, active_indices: list, m_len: int) -> np.ndarray:
        if m_len == 0:
            return np.zeros(len(active_indices))

        N_prime = self._current_n - 1
        if N_prime <= 0:
            # If removing this tuple leaves nothing, weight is the distance of an empty dataset to target
            w_val = 1 / m_len * np.abs(self._target_freqs).sum()
            return np.full(len(active_indices), w_val)

        C = self._current_counts
        T = self._target_freqs
        coeff = 1 / m_len

        # Vectorized base calculation
        base_diffs = np.abs(C / N_prime - T)
        base_sum = base_diffs.sum()

        # Diffs if the tuple MATCHES the marginal: |(C-1)/N' - T|
        hypo_diffs = np.abs((C - 1) / N_prime - T)
        # Change in sum if we remove a tuple that matches marginal m
        diff_gain = hypo_diffs - base_diffs

        weights = []
        for v_idx in active_indices:
            match_indices = self._tuple_matches[v_idx]
            if match_indices.size > 0:
                # New sum = base_sum + sum(diff_gain for matched marginals)
                w = coeff * (base_sum + diff_gain[match_indices].sum())
            else:
                w = coeff * base_sum
            weights.append(w)

        return np.array(weights)

    def _pick_best_vertex(
        self, active_indices: list, weights: np.ndarray, graph: ig.Graph, current_alpha: float
    ) -> int:
        degrees = np.array([graph.degree(v_idx) for v_idx in active_indices])
        
        # Linear normalization to [0, 1]
        nw = self._normalize(weights)
        nd = self._normalize(degrees)

        # Minimize combined score:
        # nw: smaller is better (less error)
        # 1 - nd: smaller is better (higher degree)
        ratios = (1 - current_alpha) * nw + current_alpha * (1 - nd)

        best_local_idx = np.argmin(ratios)
        return active_indices[best_local_idx]

    def _update_state(self, chosen_v: int):
        chosen_matches = self._tuple_matches[chosen_v]
        if chosen_matches.size > 0:
            self._current_counts[chosen_matches] -= 1
        self._current_n -= 1

    def _precompute_initial_state(self, dataset: Dataset, marginals: MarginalSet):
        """Precomputes initial counts, targets, and tuple matches."""
        n = len(dataset.data)
        m_len = len(marginals)

        self._current_n = n
        self._current_counts = np.zeros(m_len)
        self._target_freqs = np.array([m.target for m in marginals])

        # Relation function rho: which marginals each tuple matches
        self._tuple_matches = [[] for _ in range(n)]

        for i, m in enumerate(marginals):
            mask = m.get_mask(dataset.data)
            matching_indices = np.where(mask)[0]
            self._current_counts[i] = len(matching_indices)
            for idx in matching_indices:
                self._tuple_matches[idx].append(i)

        # Convert to numpy arrays for faster indexing
        self._tuple_matches = [np.array(m, dtype=int) for m in self._tuple_matches]

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        # Reset state before each repair call
        self._tuple_matches = []
        self._current_counts = None
        self._current_n = 0
        return super().repair(dataset, marginals)

