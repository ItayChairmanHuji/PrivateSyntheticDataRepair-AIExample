from dataclasses import dataclass

from entities.dataset import Dataset
from synthesizers.co_noise.co_noise_alg import run_co_noise


@dataclass
class CoNoise:
    num_of_iterations: int

    def run(self, dataset: Dataset) -> Dataset:
        for _ in range(self.num_of_iterations):
            dataset = self._run_iter(dataset)
        return dataset

    def _run_iter(self, dataset: Dataset) -> Dataset:
        return run_co_noise(dataset)
