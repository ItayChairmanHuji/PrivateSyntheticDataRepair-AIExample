import itertools
from dataclasses import dataclass
from typing import Tuple, List

import numpy as np
import pandas as pd

from shared.entities.dataset import Dataset
from shared.entities.marginal import Marginal, MarginalSet
from s03_marginals.src.components.obtainer import Obtainer
from s03_marginals.src.components.utility_functions.utility_function import UtilityFunction


@dataclass
class TopKObtainer(Obtainer):
    selection_budget: float
    generation_budget: float
    k: int
    utility_function: UtilityFunction
    seed: int = 42

    def obtain(self, private_dataset: Dataset, synthetic_dataset: Dataset) -> MarginalSet:
        rng = np.random.default_rng(self.seed)
        selected = self._select_top_k_marginals(
            private_dataset.data, synthetic_dataset.data, rng, private_dataset.dcs.attrs
        )
        if not selected:
            return MarginalSet(marginals=[])
        return self._generate_noisy_marginals(selected, len(private_dataset.data), rng)

    def _generate_noisy_marginals(self, selected_data, n_p, rng) -> MarginalSet:
        scale = self._calc_generation_noise_scale(len(selected_data), n_p)
        noise = rng.normal(loc=0, scale=scale, size=len(selected_data))
        marginals = []
        for i, (key, p_val) in enumerate(selected_data):
            target = np.clip(p_val + noise[i], 0.0, 1.0)
            marginals.append(Marginal(attrs=(key[0], key[1]), values=(key[2], key[3]), target=float(target)))
        return MarginalSet(marginals=marginals)

    def _calc_generation_noise_scale(self, num_selected, n_p):
        sensitivity = 1.0 / n_p if n_p > 0 else 1.0
        return (sensitivity * np.sqrt(num_selected)) / np.sqrt(2 * self.generation_budget)

    def _select_top_k_marginals(self, p_data, s_data, rng, dc_attrs) -> List:
        scale = self._calc_selection_noise_scale(p_data)
        columns = [c for c in p_data.columns if c not in dc_attrs] if dc_attrs else p_data.columns
        candidates = []
        for attr1, attr2 in itertools.combinations(columns, 2):
            candidates = self._process_pair(p_data, s_data, attr1, attr2, scale, rng, candidates)
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [(c[1], c[2]) for c in candidates[:self.k]]

    def _calc_selection_noise_scale(self, p_data):
        sensitivity = self.utility_function.sensitivity(p_data)
        return 2 * sensitivity * np.sqrt(self.k / (8 * self.selection_budget))

    def _process_pair(self, p_data, s_data, attr1, attr2, scale, rng, candidates):
        p_vals, s_vals, indices = self._align_frequencies(p_data, s_data, attr1, attr2)
        if len(p_vals) == 0: return candidates
        noisy_utils = self.utility_function(p_vals, s_vals) + rng.gumbel(0, scale, len(p_vals))
        for i, idx in enumerate(indices):
            candidates.append((noisy_utils[i], (attr1, attr2, idx[0], idx[1]), p_vals[i]))
        return self._prune_candidates(candidates)

    def _align_frequencies(self, p_data, s_data, attr1, attr2):
        p_counts = p_data[[attr1, attr2]].value_counts(normalize=True)
        s_counts = s_data[[attr1, attr2]].value_counts(normalize=True)
        idx = p_counts.index.union(s_counts.index)
        p_vals = p_counts.reindex(idx, fill_value=0.0).values
        s_vals = s_counts.reindex(idx, fill_value=0.0).values
        return p_vals, s_vals, idx

    def _prune_candidates(self, candidates):
        if len(candidates) <= 5 * self.k: return candidates
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[:2 * self.k]

