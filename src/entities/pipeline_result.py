from dataclasses import dataclass
from typing import Dict, Any
from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet

@dataclass
class PipelineResult:
    """
    Holds the results of a single pipeline execution.
    """
    private_dataset: Dataset
    synthetic_dataset: Dataset
    repaired_dataset: Dataset
    obtained_marginals: MarginalSet
    runtimes: Dict[str, float]
    metadata: Dict[str, Any] = None
