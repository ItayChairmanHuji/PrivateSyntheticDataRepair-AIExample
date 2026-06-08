from dataclasses import dataclass

import numpy as np

from .base import AlphaCalculator


@dataclass
class ConstantAlphaCalculator(AlphaCalculator):
    alpha: float = 0.5

    def calculate_alpha(self, degrees: np.ndarray, weights: np.ndarray) -> float:
        return self.alpha
