from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class UtilityFunction(ABC):
    """
    Abstract base class for utility functions used in marginal selection.
    """
    @abstractmethod
    def __call__(self, p_marg_values: np.ndarray, s_marg_values: np.ndarray) -> np.ndarray:
        """
        Calculates utility scores for a set of marginals.
        """
        pass

    @abstractmethod
    def sensitivity(self, data: pd.DataFrame) -> float:
        """
        Returns the sensitivity of the utility function.
        """
        pass
