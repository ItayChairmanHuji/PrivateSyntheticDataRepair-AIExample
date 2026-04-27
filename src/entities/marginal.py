from dataclasses import dataclass
from typing import Any, List
import pandas as pd

@dataclass(frozen=True)
class Marginal:
    """
    Represents a 2-way marginal: P(attr1=val1, attr2=val2)
    """
    attr1: str
    attr2: str
    value1: Any
    value2: Any
    target: float

    def get_mask(self, data: pd.DataFrame):
        return (data[self.attr1] == self.value1) & (data[self.attr2] == self.value2)

    def calculate_frequency(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        return len(data[self.get_mask(data)]) / len(data)

    def calculate_error(self, data: pd.DataFrame) -> float:
        freq = self.calculate_frequency(data)
        if freq == 0:
            return abs(freq - self.target) # avoid division by zero
        return abs(freq - self.target) / freq

@dataclass
class MarginalSet:
    marginals: List[Marginal]

    def __len__(self):
        return len(self.marginals)

    def __iter__(self):
        return iter(self.marginals)
