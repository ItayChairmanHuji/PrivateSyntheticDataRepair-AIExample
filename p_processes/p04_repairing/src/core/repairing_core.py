from dataclasses import dataclass
from typing import Any
from u_utilities.u_shared import Dataset, MarginalSet

@dataclass
class RepairingCore:
    """Logic: Encapsulates the repair core."""
    repairer: Any # The hydra-instantiated repairer

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        return self.repairer.repair(dataset, marginals)
