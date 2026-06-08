from abc import ABC, abstractmethod

import numpy as np


class AlphaCalculator(ABC):
    @abstractmethod
    def calculate_alpha(self, degrees: np.ndarray, weights: np.ndarray) -> float:
        pass
