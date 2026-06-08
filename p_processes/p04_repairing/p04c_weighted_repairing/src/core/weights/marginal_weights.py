import numpy as np

from u_utilities.u_shared import Dataset, MarginalSet

from .base import WeightCalculator


class MarginalWeightCalculator(WeightCalculator):
    def __init__(self, dataset: Dataset, marginals: MarginalSet):
        n = len(dataset.data)
        m_len = len(marginals)
        self.current_n = n
        self.current_counts = np.zeros(m_len)
        self.target_freqs = np.array([m.target for m in marginals])
        self.matching_matrix = np.zeros((n, m_len), dtype=bool)

        for i, m in enumerate(marginals):
            mask = m.get_mask(dataset.data)
            self.matching_matrix[:, i] = mask
            self.current_counts[i] = np.sum(mask)

    def calculate_weights(self, active_indices: np.ndarray) -> np.ndarray:
        m_len = len(self.current_counts)
        if m_len == 0 or self.current_n <= 1:
            return np.zeros(len(active_indices))

        new_size = self.current_n - 1
        base_diffs = np.abs(self.current_counts / new_size - self.target_freqs)
        hypo_diffs = np.abs((self.current_counts - 1) / new_size - self.target_freqs)
        diff_gain = hypo_diffs - base_diffs

        active_matrix = self.matching_matrix[active_indices]
        gain = active_matrix @ diff_gain
        return (base_diffs.sum() + gain) / m_len

    def update(self, chosen_v: int):
        matches = np.where(self.matching_matrix[chosen_v])[0]
        if matches.size > 0:
            self.current_counts[matches] -= 1
        self.current_n -= 1
