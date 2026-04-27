from abc import ABC, abstractmethod

import pandas as pd

from src.entities.marginal import Marginal


class VertexWeightFunction(ABC):
    @abstractmethod
    def compute(self, data: pd.DataFrame, marginals: list[Marginal]) -> list[float]:
        raise NotImplementedError
