from dataclasses import dataclass
from typing import Optional

from pandas import DataFrame

from src.entities.denial_constraints import DenialConstraints
from src.loading.violation_finder import ViolationFinder


@dataclass
class Dataset:
    """
    Core data entity representing a dataset with its associated constraints and metadata.

    Attributes:
        name: Identifier for the dataset.
        data: The actual numeric/encoded data in a Pandas DataFrame.
        dcs: Denial constraints that apply to this dataset.
        target: The target column name for ML tasks.
        mappings: A dictionary mapping column names to LabelEncoders, used for 
                  decoding categorical data back to its original string form.
    """
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
