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

    def calculate_alpha(
        self,
        graph: ig.Graph,
        active_indices: np.ndarray,
        norm_degrees: np.ndarray,
        norm_weights: np.ndarray = None,
    ) -> tuple[float, float, float]:
        if len(active_indices) == 0:
            return self.alpha_min, 0.0, 0.0

        n_active = len(active_indices)
        if n_active <= 1:
            return self.alpha_max, 0.0, 0.0

        std_degree = np.std(norm_degrees)

        if norm_weights is not None and len(norm_weights) > 0:
            std_weights = np.std(norm_weights)
        else:
            std_weights = 0.0

        if std_degree + std_weights == 0:
            alpha = 0.5
        else:
            alpha = 0.5 + 0.5 * np.tanh(std_degree - std_weights)

        # Legacy calculations for logging purposes (h and c)
        degrees = np.array(graph.degree(active_indices))
        mean_deg = np.mean(degrees)
        h = np.std(degrees) / (mean_deg + 1e-6)

        edges = graph.ecount()
        max_edges = (n_active * (n_active - 1)) / 2
        c = edges / (max_edges + 1e-6)

        return float(alpha), float(h), float(c)
