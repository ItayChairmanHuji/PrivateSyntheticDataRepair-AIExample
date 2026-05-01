from dataclasses import dataclass
from typing import Optional

from pandas import DataFrame

from src.entities.denial_constraints import DenialConstraints
from src.loading.violation_finder import ViolationFinder


@dataclass
class Dataset:
    name: str
    data: DataFrame
    dcs: DenialConstraints
    target: str
    mappings: Optional[dict] = None

    def __len__(self):
        return len(self.data)

    def get_violations(self) -> DataFrame:
        finder = ViolationFinder()
        return finder.find_violations(self.data, self.dcs)
