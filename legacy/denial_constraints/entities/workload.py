from dataclasses import dataclass
from typing import Callable

from pandas import DataFrame


@dataclass
class Workload:
    first: DataFrame
    second: DataFrame
    query: str

    def __iter__(self):
        return iter((self.first, self.second, self.query))

    def run_both(self, func: Callable, keep_type=True):
        return Workload(
            first=func(self.first, 0),
            second=func(self.second, 1),
            query=self.query,
        ) if keep_type else (func(self.first, 0), func(self.second, 1))
