from abc import ABC, abstractmethod
from src.entities.dataset import Dataset

class Synthesizer(ABC):
    """
    Abstract base class for all synthesizers.
    """
    @abstractmethod
    def synthesize(self, dataset: Dataset) -> Dataset:
        """
        Takes a private dataset and returns a synthetic version of it.
        """
        pass
