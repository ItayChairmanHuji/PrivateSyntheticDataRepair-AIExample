from abc import ABC, abstractmethod
from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet

class Obtainer(ABC):
    """
    Abstract base class for all marginal obtainers.
    """
    @abstractmethod
    def obtain(self, private_dataset: Dataset, synthetic_dataset: Dataset) -> MarginalSet:
        """
        Takes private and synthetic datasets and returns a set of k marginals.
        """
        pass
