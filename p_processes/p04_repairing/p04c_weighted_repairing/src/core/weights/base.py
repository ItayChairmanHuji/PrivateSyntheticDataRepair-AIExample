from abc import ABC, abstractmethod

import numpy as np


class WeightCalculator(ABC):
    @abstractmethod
    def calculate_weights(self, active_indices: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def update(self, chosen_v: int):
        pass
