from abc import ABC, abstractmethod
from u_utilities.u_shared import Dataset, MarginalSet

class Repairer(ABC):
    """
    Abstract base class for all repairers.
    """
    @abstractmethod
    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        """
        Takes a synthetic dataset and a set of marginals and returns a repaired dataset.
        """
        pass
