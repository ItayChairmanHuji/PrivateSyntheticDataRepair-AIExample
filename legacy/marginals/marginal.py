from dataclasses import dataclass
from typing import Any

from pandas import DataFrame


@dataclass
class Marginal:
    attr1: str
    attr2: str
    value1: Any
    value2: Any
    target: float

    def mask(self, data: DataFrame):
        return (data[self.attr1] == self.value1) & (data[self.attr2] == self.value2)

    def indices(self, data: DataFrame):
        return data[self.mask(data)].index

    def calculate(self, data: DataFrame):
        return len(data[self.mask(data)]) / len(data)

    def calculate_error(self, data: DataFrame):
        current = self.calculate(data)
        return abs(current - self.target) / current
