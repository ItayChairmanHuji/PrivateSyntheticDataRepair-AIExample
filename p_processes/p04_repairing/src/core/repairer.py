from abc import ABC, abstractmethod
from u_utilities.u_shared import Dataset, MarginalSet

class Repairer(ABC):
    @abstractmethod
    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:    
        pass
