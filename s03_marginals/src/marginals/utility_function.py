from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class UtilityFunction(ABC):
    @abstractmethod
    def __call__(self, p_marg_values: np.ndarray, s_marg_values: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def sensitivity(self, data: pd.DataFrame) -> float:
        pass
