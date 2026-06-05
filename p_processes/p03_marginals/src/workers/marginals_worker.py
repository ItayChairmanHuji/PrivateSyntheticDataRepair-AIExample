from dataclasses import dataclass
from typing import Any
from u_utilities.u_shared import Dataset

@dataclass
class MarginalsWorker:
    """Worker: Encapsulates the marginal calculation logic."""
    calculator: Any # The hydra-instantiated calculator

    def calculate(self, dataset: Dataset) -> Any:
        return self.calculator.calculate(dataset)
