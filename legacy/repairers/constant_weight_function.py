from dataclasses import dataclass

import pandas as pd

from src.data_repair.vertex_cover.weight_function import VertexWeightFunction
from src.entities.marginal import Marginal


@dataclass(slots=True)
class ConstantWeightFunction(VertexWeightFunction):
    value: float = 1.0

    def compute(self, data: pd.DataFrame, marginals: list[Marginal]) -> list[float]:
        del marginals
        return [self.value for _ in range(data.shape[0])]
