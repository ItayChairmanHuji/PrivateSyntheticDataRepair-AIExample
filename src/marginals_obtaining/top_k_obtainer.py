import itertools
from dataclasses import dataclass
from typing import Dict, Tuple, List

import numpy as np
import pandas as pd

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
    seed: int = 42

    def obtain(
        self, private_dataset: Dataset, synthetic_dataset: Dataset
    ) -> MarginalSet:
        p_data = private_dataset.data
        s_data = synthetic_dataset.data
        
        # Initialize random generator with the seed
        rng = np.random.default_rng(self.seed)

        # 1. Compute and select top-k marginals using Exponential Mechanism (Gumbel trick)
        # We do this per attribute pair to save memory.
        selected_marginals_data = self._select_top_k_marginals(p_data, s_data, rng)
        
        if not selected_marginals_data:
            return MarginalSet(marginals=[])

        # 2. Generation: Add noise to the private frequencies of selected marginals
        num_selected = len(selected_marginals_data)
        generation_sensitivity = 1.0 / len(p_data) if len(p_data) > 0 else 1.0
        generation_noise_scale = (
            generation_sensitivity * np.sqrt(num_selected)
        ) / np.sqrt(2 * self.generation_budget)
        
        gen_noise = rng.normal(
            loc=0, scale=generation_noise_scale, size=num_selected
        )

        marginals = []
        for i, (key, p_val) in enumerate(selected_marginals_data):
            noisy_val = np.clip(p_val + gen_noise[i], 0.0, 1.0)
            marginals.append(
                Marginal(
                    attrs=(key[0], key[1]), values=(key[2], key[3]), target=float(noisy_val)
                )
            )

        return MarginalSet(marginals=marginals)

    def _select_top_k_marginals(self, p_data: pd.DataFrame, s_data: pd.DataFrame, rng: np.random.Generator) -> List[Tuple[Tuple, float]]:
        """
        Computes utilities and selects top-k marginals without keeping all in memory.
        """
        num_to_select = self.k
        selection_sensitivity = self.utility_function.sensitivity(p_data)
        selection_noise_scale = (
            2
            * selection_sensitivity
            * np.sqrt(num_to_select / (8 * self.selection_budget))
        )
        
        candidates = [] # List of (noisy_utility, key, p_val)
        columns = p_data.columns

        for attr1, attr2 in itertools.combinations(columns, 2):
            # Vectorized computation of frequencies for the attribute pair
            p_counts = p_data[[attr1, attr2]].value_counts(normalize=True)
            s_counts = s_data[[attr1, attr2]].value_counts(normalize=True)
            
            # Use index union to align p and s frequencies
            all_indices = p_counts.index.union(s_counts.index)
            p_vals = p_counts.reindex(all_indices, fill_value=0.0).values
            s_vals = s_counts.reindex(all_indices, fill_value=0.0).values
            
            if len(p_vals) == 0:
                continue
                
            # Vectorized utility and noise calculation
            utilities = self.utility_function(p_vals, s_vals)
            noise = rng.gumbel(loc=0.0, scale=selection_noise_scale, size=len(utilities))
            noisy_utilities = utilities + noise
            
            # Store candidates for the global top-K selection
            for i, idx_val in enumerate(all_indices):
                key = (attr1, attr2, idx_val[0], idx_val[1])
                candidates.append((noisy_utilities[i], key, p_vals[i]))
            
            # Prune candidates to keep memory usage bounded
            if len(candidates) > 5 * self.k:
                candidates.sort(key=lambda x: x[0], reverse=True)
                candidates = candidates[:2 * self.k]

        # Final selection of top K
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_k = candidates[:num_to_select]
        
        return [(c[1], c[2]) for c in top_k]

    def _compute_all_2way_marginals(self, data: pd.DataFrame) -> Dict[Tuple, float]:
        """Deprecated: Use _select_top_k_marginals instead for memory efficiency."""
        marginals = {}
        columns = data.columns
        for attr1, attr2 in itertools.combinations(columns, 2):
            counts = data[[attr1, attr2]].value_counts(normalize=True).items()
            for (val1, val2), freq in counts:
                marginals[(attr1, attr2, val1, val2)] = freq
        return marginals
