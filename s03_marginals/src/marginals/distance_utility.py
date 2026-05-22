import numpy as np
import pandas as pd
from s03_marginals.src.marginals.utility_function import UtilityFunction

class DistanceUtility(UtilityFunction):
    def __call__(self, p_marg_values: np.ndarray, s_marg_values: np.ndarray) -> np.ndarray:
        return np.abs(p_marg_values - s_marg_values)

    def sensitivity(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 1.0
        return 1.0 / len(data)
