from dataclasses import dataclass

import numpy as np

from .base import AlphaCalculator


@dataclass
class AdaptiveAlphaCalculator(AlphaCalculator):
    def calculate_alpha(self, degrees: np.ndarray, weights: np.ndarray) -> float:
        std_degree = np.std(degrees)
        std_weights = np.std(weights)
        alpha = 0.5 + 0.5 * np.tanh(std_degree - std_weights)
        return float(alpha)
