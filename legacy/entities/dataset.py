from dataclasses import dataclass
from functools import cached_property

from pandas import DataFrame

from denial_constraints.violation_finding.violations_finder import find_violations
from src.entities.denial_constraints import DenialConstraints


@dataclass
class Dataset:
    name: str
    data: DataFrame
    dcs: DenialConstraints
    target: str

    @cached_property
    def dcs_violations(self):
        return find_violations(self.data, self.dcs)

    def __len__(self):
        return len(self.data)