from dataclasses import dataclass, field
from typing import List, Optional

import igraph as ig
import numpy as np

from u_utilities.u_repair.src.adaptive_alpha_calculator import AdaptiveAlphaCalculator
from u_utilities.u_repair.src.vertex_cover_repairer import VertexCoverRepairer
from u_utilities.u_shared import Dataset, MarginalSet

@dataclass
class WeightedVCRepairer(VertexCoverRepairer):
    """
    Highly optimized Weighted Vertex Cover repair.
    """

    alpha: float
    use_adaptive_alpha: bool = True
    use_auto_alpha: bool = False

    _auto_alpha: Optional[float] = field(init=False, default=None)
    _alpha_calculator: Optional[AdaptiveAlphaCalculator] = field(
        init=False, default=None
    )
    _matching_matrix: Optional[np.ndarray] = field(init=False, default=None)
    _current_counts: Optional[np.ndarray] = field(init=False, default=None)
    _current_n: int = field(init=False, default=0)
    iteration_stats: List[dict] = field(init=False, default_factory=list)

    def _select_vertex(
        self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet
    ) -> int:
        import time
        if self._matching_matrix is None:
            self._init_state(dataset, marginals, graph)

        active_indices = graph.vs.select(_degree_gt=0)
        if len(active_indices) == 0:
            return -1

        t0 = time.perf_counter_ns()
        weights = self._calculate_weights(active_indices, len(marginals))
        self.profiler["weight_calc_ns"] = self.profiler.get("weight_calc_ns", 0) + (time.perf_counter_ns() - t0)
        
        degrees = graph.degree(active_indices)
        
        norm_weights = self._normalize(weights)
        norm_degrees = self._normalize(degrees)

        t1 = time.perf_counter_ns()
        alpha, h, c = self._get_alpha_metrics(graph, active_indices, norm_degrees, norm_weights)
        self.profiler["alpha_metrics_ns"] = self.profiler.get("alpha_metrics_ns", 0) + (time.perf_counter_ns() - t1)

        if len(self.iteration_stats) % 100 == 0:
            self.iteration_stats.append({
                "iteration": len(self.iteration_stats),
                "alpha": alpha,
                "hubbiness": h,
                "connectivity": c,
                "n_active": len(active_indices),
                "n_edges": graph.ecount()
            })

        chosen_v = self._pick_best_vertex(active_indices, norm_weights, norm_degrees, alpha)
        self._update_state(chosen_v)
        return chosen_v

    def _init_state(self, dataset: Dataset, marginals: MarginalSet, graph: ig.Graph):
        self._precompute_initial_state(dataset, marginals)
        if self.use_auto_alpha:
            self._auto_alpha = self._calculate_auto_alpha(graph)
        elif self.use_adaptive_alpha:
            self._alpha_calculator = AdaptiveAlphaCalculator()

    def _calculate_auto_alpha(self, graph: ig.Graph) -> float:
        degrees = np.array(graph.degree())
        mean_deg = np.mean(degrees)
        if mean_deg == 0:
            return 0.0
        cv = np.std(degrees) / (mean_deg + 1e-8)
        return float(cv / (cv + 1))

    def _get_alpha_metrics(self, graph: ig.Graph, active_indices: np.ndarray, norm_degrees: np.ndarray, norm_weights: np.ndarray) -> tuple[float, float, float]:
        if self.use_auto_alpha and self._auto_alpha is not None:
            return self._auto_alpha, 0.0, 0.0
        if self.use_adaptive_alpha and self._alpha_calculator:
            return self._alpha_calculator.calculate_alpha(graph, active_indices, norm_degrees, norm_weights)
        return self.alpha, 0.0, 0.0

    def _calculate_weights(self, active_indices: np.ndarray, m_len: int) -> np.ndarray:
        if m_len == 0:
            return np.zeros(len(active_indices))

        current_counts = self._current_counts
        target_freqs = self._target_freqs

        if current_counts is None or target_freqs is None or self._matching_matrix is None:
            return np.zeros(len(active_indices))

        if self._current_n <= 1:
            return self._handle_small_n(active_indices, m_len, target_freqs)

        diff_gain, base_sum = self._compute_base_metrics(
            m_len, current_counts, target_freqs
        )
        
        active_matrix = self._matching_matrix[active_indices]
        gain = active_matrix @ diff_gain
        return (base_sum + gain) / m_len

    def _handle_small_n(
        self, active_indices: np.ndarray, m_len: int, target_freqs: np.ndarray
    ) -> np.ndarray:
        val = 1 / m_len * np.abs(target_freqs).sum()
        return np.full(len(active_indices), val)

    def _compute_base_metrics(
        self, m_len: int, current_counts: np.ndarray, target_freqs: np.ndarray
    ):
        N_prime = self._current_n - 1
        base_diffs = np.abs(current_counts / (N_prime + 1e-8) - target_freqs)
        hypo_diffs = np.abs((current_counts - 1) / (N_prime + 1e-8) - target_freqs)
        return hypo_diffs - base_diffs, base_diffs.sum()

    def _pick_best_vertex(
        self,
        active_indices: np.ndarray,
        norm_weights: np.ndarray,
        norm_degrees: np.ndarray,
        alpha: float,
    ) -> int:
        nw = norm_weights
        nd = -norm_degrees
        ratios = (1 - alpha) * nw + alpha * nd
        return int(active_indices[int(np.argmin(ratios))])

    def _update_state(self, chosen_v: int):
        if self._matching_matrix is not None:
            matches = np.where(self._matching_matrix[chosen_v])[0]
            if matches.size > 0 and self._current_counts is not None:
                self._current_counts[matches] -= 1
        self._current_n -= 1

    def _precompute_initial_state(self, dataset: Dataset, marginals: MarginalSet):
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

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        self._matching_matrix = None
        self._current_counts = None
        self._current_n = 0
        self.iteration_stats = []
        self._auto_alpha = None
        return super().repair(dataset, marginals)
