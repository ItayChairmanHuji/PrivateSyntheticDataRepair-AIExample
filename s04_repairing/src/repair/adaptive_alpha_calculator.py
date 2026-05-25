from dataclasses import dataclass

import igraph as ig
import numpy as np


@dataclass
class AdaptiveAlphaCalculator:
    """
    Calculates an adaptive alpha parameter based on graph topology.
    """

    alpha_min: float = 0.1
    alpha_max: float = 1.0
    connectivity_steepness: float = 2.0
    gamma: float = 2.0

    def calculate_alpha(self, graph: ig.Graph, active_indices: list) -> tuple[float, float, float]:
        if not active_indices:
            return self.alpha_min, 0.0, 0.0
        if len(active_indices) <= 2:
            return self.alpha_max, 0.0, 1.0

        h, c, danger = self._calculate_metrics(graph, active_indices)
        alpha = self._combine_alpha(danger)
        return alpha, h, c

    def _calculate_metrics(self, graph: ig.Graph, active_indices: list) -> tuple[float, float, float]:
        degrees = np.array([graph.degree(v_idx) for v_idx in active_indices])
        hubbiness = self._calculate_hubbiness(degrees, len(active_indices))
        connectivity = self._calculate_connectivity(degrees, len(active_indices))
        # New formula: Danger only comes from hubs, scaled by connectivity (density)
        danger = (1 - (1 - hubbiness) ** self.gamma) * connectivity
        return hubbiness, connectivity, danger

    def _calculate_hubbiness(self, degrees: np.ndarray, n: int) -> float:
        denominator = (n - 1) * (n - 2)
        if denominator <= 0:
            return 0.0
        d_max = np.max(degrees)
        hubbiness = np.sum(d_max - degrees) / denominator
        return float(np.clip(hubbiness, 0, 1))

    def _calculate_connectivity(self, degrees: np.ndarray, n: int) -> float:
        avg_degree = np.sum(degrees) / n
        exp_term = np.exp(-self.connectivity_steepness * (avg_degree - 1.0))
        return float(1.0 / (1.0 + exp_term))

    def _combine_alpha(self, danger: float) -> float:
        alpha = self.alpha_min + (self.alpha_max - self.alpha_min) * danger
        return float(np.clip(alpha, self.alpha_min, self.alpha_max))
