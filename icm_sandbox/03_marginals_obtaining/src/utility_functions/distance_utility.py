import numpy as np
import pandas as pd
from src.marginals_obtaining.utility_functions.utility_function import UtilityFunction

class DistanceUtility(UtilityFunction):
    """
    Utility function based on the absolute distance between private and synthetic marginal frequencies.
    """
    def __call__(self, p_marg_values: np.ndarray, s_marg_values: np.ndarray) -> np.ndarray:
        return np.abs(p_marg_values - s_marg_values)

    def sensitivity(self, data: pd.DataFrame) -> float:
        # For frequency distance, sensitivity is 1/N
        if len(data) == 0:
            return 1.0
        return 1.0 / len(data)
