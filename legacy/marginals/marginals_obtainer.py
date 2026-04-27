import itertools
from collections import namedtuple
from dataclasses import dataclass

import numpy as np
from pandas import DataFrame
from scipy.stats import gumbel_r

from marginals.marginal import Marginal
from marginals.utility_functions.utility_function import UtilityFunction

MarginalKey = namedtuple("MarginalKey", ["attr1", "attr2", "value1", "value2"])
SelectionDict = dict[MarginalKey, float]


@dataclass
class MarginalsObtainer:
    selection_budget: float
    generation_budget: float
    num_of_marginals: int
    utility_function: UtilityFunction

    def obtain(self, p_data: DataFrame, s_data: DataFrame):
        generation_sensitivity = 1 / len(p_data)
        selection_sensitivity = self.utility_function.sensitivity(p_data)
        p_marg = self._compute_marginals(p_data)
        s_marg = self._compute_marginals(s_data)
        keys, noisy_utility = self._add_selection_nosie(p_marg, s_marg, selection_sensitivity)
        marginals = self._select_marginals(keys, noisy_utility)
        return self._generate_marginals(marginals, p_marg, generation_sensitivity)

    @staticmethod
    def _compute_marginals(data: DataFrame) -> SelectionDict:
        marginals = {}
        attrs = itertools.combinations(data.columns, 2)
        for attr1, attr2 in attrs:
            pair_counts = data[[attr1, attr2]].value_counts(dropna=False, normalize=True).items()
            for (val1, val2), freq in pair_counts:
                key = MarginalKey(attr1=attr1, attr2=attr2, value1=val1, value2=val2)
                marginals[key] = freq
        return marginals

    def _add_selection_nosie(self, p_marg: SelectionDict, s_marg: SelectionDict, sensitivity: float):
        keys = list(p_marg.keys())
        utility = self._selection_utility(p_marg, s_marg, keys)
        noise = self._selection_noise(len(utility), sensitivity)
        return keys, utility + noise

    def _selection_utility(self, p_marg: SelectionDict, s_marg: SelectionDict, keys: list):
        p_array = np.array([p_marg[key] for key in keys])
        s_array = np.array([s_marg.get(key, 0.0) for key in keys])
        return self.utility_function(p_array, s_array)

    def _selection_noise(self, size: int, sensitivity: float):
        noise_scale = 2 * sensitivity * np.sqrt(self.num_of_marginals / (8 * self.selection_budget))
        return gumbel_r.rvs(loc=0, scale=noise_scale, size=size)

    def _select_marginals(self, keys: list, scores: np.ndarray):
        sorted_scores_indices = np.argsort(scores)
        top_k = sorted_scores_indices[-self.num_of_marginals:]
        return keys[top_k]

    def _generate_marginals(self, keys: list[MarginalKey], marginals: SelectionDict, sensitivity: float):
        marginals_values = np.array([marginals[key] for key in keys])
        noise = self._generation_noise(sensitivity)
        values = marginals_values + noise
        return [self._generate_marginal(key, value) for key, value in zip(keys, list(values))]

    @staticmethod
    def _generate_marginal(key: MarginalKey, value: float):
        return Marginal(
            attr1=key.attr1,
            attr2=key.attr2,
            value1=key.value1,
            value2=key.value2,
            target=value
        )

    def _generation_noise(self, sensitivity: float):
        noise_scale = sensitivity * np.sqrt(self.num_of_marginals) / (np.sqrt(2 * self.generation_budget))
        return np.random.normal(loc=0, scale=noise_scale, size=self.num_of_marginals)
