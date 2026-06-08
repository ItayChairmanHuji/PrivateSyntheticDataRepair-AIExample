from dataclasses import dataclass
from typing import Optional

from pandas import DataFrame

from . import compactor

from .compact_data import CompactData
from .denial_constraints import DenialConstraints
from .violations import ViolationSet


@dataclass
class Dataset:
    name: str
    data: DataFrame
    dcs: DenialConstraints
    target: str
    mappings: Optional[dict] = None
    _compact: Optional[CompactData] = None

    def compact(self) -> CompactData:
        if self._compact is None:
            self._compact = compactor.compact_data(self.data, sorted(self.dcs.attrs))
        return self._compact

    def get_violations(self) -> ViolationSet:
        from u_utilities.u_violation_finder import ViolationFinder
        return ViolationFinder().find_violations(self)

    def __len__(self):
        return len(self.data)
