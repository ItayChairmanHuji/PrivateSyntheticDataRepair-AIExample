import numpy as np
from typing import List, Tuple
from u_utilities.u_shared import Marginal, MarginalSet

class MarginalGenerator:
    """Worker: Generates noisy marginals from selected candidates."""

    def generate_noisy(
        self, 
        selected: List[Tuple], 
        n_p: int, 
        budget: float, 
        rng: np.random.Generator
    ) -> MarginalSet:
        """Adds Laplace/Gaussian noise to marginal targets."""
        scale = self._calc_noise_scale(len(selected), n_p, budget)
        noise = rng.normal(loc=0, scale=scale, size=len(selected))
        marginals = []
        for i, (key, p_val) in enumerate(selected):
            target = np.clip(p_val + noise[i], 0.0, 1.0)
            marginals.append(Marginal(
                attrs=(key[0], key[1]), 
                values=(key[2], key[3]), 
                target=float(target)
            ))
        return MarginalSet(marginals=marginals)

    def _calc_noise_scale(self, num_selected, n_p, budget):
        sensitivity = 1.0 / n_p if n_p > 0 else 1.0
        return (sensitivity * np.sqrt(num_selected)) / np.sqrt(2 * budget)
