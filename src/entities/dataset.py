
from dataclasses import dataclass
from pandas import DataFrame
from src.entities.denial_constraints import DenialConstraints

@dataclass
class Dataset:
    name: str
    data: DataFrame
    dcs: DenialConstraints
    target: str

    def __len__(self):
        return len(self.data)

@dataclass
class DatasetWithViolations(Dataset):
    mappings: dict = None

    def get_violations(self) -> DataFrame:
        from src.loading.violation_finder import ViolationFinder
        finder = ViolationFinder()
        return finder.find_violations(self.data, self.dcs)

    @property
    def violations(self) -> DataFrame:
        """
        Property for backward compatibility.
        NOTE: This is no longer cached to ensure accuracy during iterative repair.
        """
        return self.get_violations()
