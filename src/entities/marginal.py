from dataclasses import dataclass
from typing import Any, List, Tuple

import pandas as pd


@dataclass(frozen=True)
class Marginal:
    """
    Represents a generalized marginal: P(attr_1=val_1, ..., attr_k=val_k)
    """
    attrs: Tuple[str, ...]
    values: Tuple[Any, ...]
    target: float

    def get_mask(self, data: pd.DataFrame):
        """Returns a boolean mask for rows matching all (attr, value) pairs."""
        if not self.attrs:
            return pd.Series(True, index=data.index)
        
        mask = (data[self.attrs[0]] == self.values[0])
        for i in range(1, len(self.attrs)):
            mask &= (data[self.attrs[i]] == self.values[i])
        return mask

    def calculate_frequency(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        return len(data[self.get_mask(data)]) / len(data)

    def calculate_error(self, data: pd.DataFrame) -> float:
        freq = self.calculate_frequency(data)
        distance = abs(freq - self.target)
        # Use a small epsilon to avoid division by zero spikes, 
        # or just return distance if freq is 0.
        return distance / freq if freq != 0 else distance

    def calculate_distance(self, data: pd.DataFrame) -> float:
        freq = self.calculate_frequency(data)
        return abs(freq - self.target)


@dataclass
class MarginalSet:
    marginals: List[Marginal]

    def __len__(self):
        return len(self.marginals)

    def __iter__(self):
        return iter(self.marginals)
