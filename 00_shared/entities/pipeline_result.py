from dataclasses import dataclass
from typing import Any, Dict

from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet


@dataclass
class PipelineResult:
    private_dataset: Dataset
    synthetic_dataset: Dataset
    repaired_dataset: Dataset
    obtained_marginals: MarginalSet
    runtimes: Dict[str, float]
    metadata: Dict[str, Any] = None
