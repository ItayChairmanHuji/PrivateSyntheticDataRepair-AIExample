from dataclasses import dataclass
from typing import Optional
from pandas import DataFrame
from .denial_constraints import DenialConstraints

@dataclass
class Dataset:
    name: str
    data: DataFrame
    dcs: DenialConstraints
    target: str
    mappings: Optional[dict] = None

    def __len__(self):
        return len(self.data)

