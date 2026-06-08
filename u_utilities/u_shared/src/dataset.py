from dataclasses import dataclass, field
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
    _compact: dict = field(default_factory=dict)

    def compact(self, attributes: Optional[list] = None) -> CompactData:
        attrs = sorted(attributes) if attributes else sorted(self.dcs.attrs)
        key = "_".join(attrs)
        if key not in self._compact:
            self._compact[key] = compactor.compact_data(self.data, attrs)
        return self._compact[key]

    def get_violations(self) -> ViolationSet:
        from u_utilities.u_violation_finder import ViolationFinder
        return ViolationFinder().find_violations(self)

    def __len__(self):
        return len(self.data)
