import numpy as np
import pandas as pd
from ..enums import ErrorMetric

class MarginalError:
    """Worker: Measures distance between marginal sets or values."""

    def compute(
        self, 
        p_vals: np.ndarray, 
        s_vals: np.ndarray, 
        metric: ErrorMetric = ErrorMetric.ABS
    ) -> np.ndarray:
        """Computes the error between two arrays of marginal values."""
        match metric:
            case ErrorMetric.ABS:
                return np.abs(p_vals - s_vals)
            case ErrorMetric.RMSE:
                return np.sqrt((p_vals - s_vals)**2)
            case _:
                raise ValueError(f"Unsupported metric: {metric}")

    def sensitivity(self, data: pd.DataFrame) -> float:
        """Computes the sensitivity of the error function for DP selection."""
        if len(data) == 0:
            return 1.0
        return 1.0 / len(data)
