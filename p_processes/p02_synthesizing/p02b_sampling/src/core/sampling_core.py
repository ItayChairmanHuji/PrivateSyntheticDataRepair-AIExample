from dataclasses import dataclass
from typing import Any, Optional
from u_utilities.u_shared import Dataset

@dataclass
class SamplingCore:
    """Logic: Encapsulates the sampling core."""
    sampler: Any # The hydra-instantiated sampler

    def sample(self, model: Any, private_dataset: Dataset, size: Optional[int] = None) -> Dataset:
        gen_size = size if size is not None else len(private_dataset.data)
        synthetic_dataset = self.sampler.sample(model, private_dataset, gen_size)
        return synthetic_dataset
