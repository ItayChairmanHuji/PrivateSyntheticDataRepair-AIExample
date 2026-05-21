from abc import ABC, abstractmethod
from shared.entities.dataset import Dataset

class Loader(ABC):
    @abstractmethod
    def load(self) -> Dataset:
        pass

