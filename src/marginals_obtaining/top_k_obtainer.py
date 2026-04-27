import itertools
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple
from scipy.stats import gumbel_r

from src.entities.dataset import Dataset
from src.entities.marginal import Marginal, MarginalSet
from src.marginals_obtaining.obtainer import Obtainer
from src.marginals_obtaining.utility_functions.utility_function import UtilityFunction

@dataclass
class TopKObtainer(Obtainer):
    selection_budget: float
    generation_budget: float
    k: int
    utility_function: UtilityFunction

    def obtain(self, private_dataset: Dataset, synthetic_dataset: Dataset) -> MarginalSet:
        p_data = private_dataset.data
        s_data = synthetic_dataset.data

        # 1. Compute all 2-way marginals for private and synthetic data
        p_marginals_freq = self._compute_all_2way_marginals(p_data)
        s_marginals_freq = self._compute_all_2way_marginals(s_data)

        # Ensure all keys from p are in s (default to 0.0)
        all_keys = list(p_marginals_freq.keys())
        p_values = np.array([p_marginals_freq[k] for k in all_keys])
        s_values = np.array([s_marginals_freq.get(k, 0.0) for k in all_keys])

        # 2. Selection using Exponential Mechanism (implemented via Gumbel trick)
        num_to_select = min(self.k, len(all_keys))
        if num_to_select == 0:
            return MarginalSet(marginals=[])

        selection_sensitivity = self.utility_function.sensitivity(p_data)
        utilities = self.utility_function(p_values, s_values)
        
        # Noise scale for selection
        selection_noise_scale = (2 * selection_sensitivity * num_to_select) / self.selection_budget
        noise = np.random.gumbel(loc=0.0, scale=selection_noise_scale, size=len(utilities))
        
        noisy_utilities = utilities + noise
        top_k_indices = np.argsort(noisy_utilities)[-num_to_select:]
        selected_keys = [all_keys[i] for i in top_k_indices]

        # 3. Generation: Add noise to the private frequencies of selected marginals
        generation_sensitivity = 1.0 / len(p_data) if len(p_data) > 0 else 1.0
        generation_noise_scale = (generation_sensitivity * np.sqrt(num_to_select)) / np.sqrt(2 * self.generation_budget)
        gen_noise = np.random.normal(loc=0, scale=generation_noise_scale, size=num_to_select)
        
        selected_p_values = np.array([p_marginals_freq[k] for k in selected_keys])
        noisy_p_values = selected_p_values + gen_noise
        # Clip frequencies to [0, 1]
        noisy_p_values = np.clip(noisy_p_values, 0.0, 1.0)

        # 4. Create Marginal objects
        marginals = []
        for key, val in zip(selected_keys, noisy_p_values):
            marginals.append(Marginal(
                attr1=key[0],
                attr2=key[1],
                value1=key[2],
                value2=key[3],
                target=float(val)
            ))

        return MarginalSet(marginals=marginals)

    def _compute_all_2way_marginals(self, data: pd.DataFrame) -> Dict[Tuple, float]:
        """
        Computes all 2-way marginal frequencies.
        Returns a dict mapping (attr1, attr2, val1, val2) -> frequency.
        """
        marginals = {}
        columns = data.columns
        for attr1, attr2 in itertools.combinations(columns, 2):
            counts = data[[attr1, attr2]].value_counts(normalize=True).items()
            for (val1, val2), freq in counts:
                marginals[(attr1, attr2, val1, val2)] = freq
        return marginals
