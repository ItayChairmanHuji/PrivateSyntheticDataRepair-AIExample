import numpy as np
import igraph as ig

class AdaptiveAlphaCalculator:
    """
    Calculates an adaptive alpha parameter based on graph topology.
    Uses Freeman's Centralization Index for Hubbiness and Percolation Theory for Connectivity.
    """
    def __init__(self, alpha_min: float = 0.1, alpha_max: float = 1.0, connectivity_steepness: float = 2.0):
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.k = connectivity_steepness

    def calculate_alpha(self, graph: ig.Graph, active_indices: list) -> float:
        if not active_indices:
            return self.alpha_min
            
        n = len(active_indices)
        if n <= 2:
            return self.alpha_max

        degrees = np.array([graph.degree(v_idx) for v_idx in active_indices])
        d_max = np.max(degrees)
        d_sum = np.sum(degrees)
        
        # 1. Hubbiness (Freeman's Centralization Index)
        # Normalized between 0 and 1.
        # H = sum(d_max - d_i) / ((n-1)(n-2))
        denominator = (n - 1) * (n - 2)
        if denominator > 0:
            hubbiness = np.sum(d_max - degrees) / denominator
            # Clip to [0, 1] as precision errors or graph types might occasionally drift
            hubbiness = np.clip(hubbiness, 0, 1)
        else:
            hubbiness = 0.0

        # 2. Connectivity (Percolation Proxy via Average Degree)
        # avg_degree = 2 * edges / nodes
        avg_degree = d_sum / n
        
        # Logistic/Sigmoid function centered around avg_degree = 1 (Percolation threshold)
        # C = 1 / (1 + exp(-k * (avg_degree - 1)))
        connectivity = 1.0 / (1.0 + np.exp(-self.k * (avg_degree - 1.0)))
        
        # 3. Combined Alpha
        # Intuition: alpha should be low (Utility-heavy) when Connectivity is high.
        # alpha should be high (Efficiency-heavy) when Hubbiness is high and Connectivity is low.
        
        # Refined formula: alpha = 0.5 + 0.5 * (Hubbiness - Connectivity)
        # Shifted to respect alpha_min and alpha_max
        raw_alpha = 0.5 + 0.5 * (hubbiness - connectivity)
        
        # Map to [alpha_min, alpha_max]
        alpha = self.alpha_min + (self.alpha_max - self.alpha_min) * raw_alpha
        
        return np.clip(alpha, self.alpha_min, self.alpha_max)
