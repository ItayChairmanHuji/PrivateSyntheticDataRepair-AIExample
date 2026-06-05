from dataclasses import dataclass
from typing import Any
from u_utilities.u_shared import Dataset
from u_utilities.u_shared.marginal import MarginalSet

@dataclass
class RepairingWorker:
    """Worker: Encapsulates the repair logic."""
    repairer: Any # The hydra-instantiated repairer

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        return self.repairer.repair(dataset, marginals)
