from abc import ABC, abstractmethod
from u_utilities.u_shared import Dataset

class Synthesizer(ABC):
    @abstractmethod
    def synthesize(self, dataset: Dataset) -> Dataset:
        pass

class ModelTrainer(ABC):
    @abstractmethod
    def train(self, dataset: Dataset) -> any:
        pass

class ModelSampler(ABC):
    @abstractmethod
    def sample(self, model: any, dataset: Dataset, size: int) -> Dataset:
        pass
