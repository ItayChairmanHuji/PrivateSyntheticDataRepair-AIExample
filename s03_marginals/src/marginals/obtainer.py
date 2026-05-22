from abc import ABC, abstractmethod
from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet

class Obtainer(ABC):
    @abstractmethod
    def obtain(self, private_dataset: Dataset, synthetic_dataset: Dataset) -> MarginalSet:
        pass
