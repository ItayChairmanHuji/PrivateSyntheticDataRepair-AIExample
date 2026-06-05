from abc import ABC, abstractmethod
from u_utilities.u_shared.dataset import Dataset
from u_utilities.u_shared.marginal import MarginalSet

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

