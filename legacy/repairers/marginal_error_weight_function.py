from dataclasses import dataclass

import pandas as pd

from src.data_repair.marginal_metrics import tuple_removal_impacts
from src.data_repair.vertex_cover.weight_function import VertexWeightFunction
from src.entities.marginal import Marginal


@dataclass(slots=True)
class MarginalErrorWeightFunction(VertexWeightFunction):
    def compute(self, data: pd.DataFrame, marginals: list[Marginal]) -> list[float]:
        return tuple_removal_impacts(data, marginals)
