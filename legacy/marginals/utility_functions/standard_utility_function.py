import numpy as np
from pandas import DataFrame

from marginals.utility_functions.utility_function import UtilityFunction


class StandardUtilityFunction(UtilityFunction):
    def sensitivity(self, data: DataFrame):
        return 1 / len(data)

    def __call__(self, p_marg, s_marg):
        return np.abs(p_marg - s_marg)
