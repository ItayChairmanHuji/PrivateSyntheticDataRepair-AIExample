import json
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager, DataMode
from u_utilities.u_shared import Dataset, MarginalSet

@dataclass
class RepairingEngine:
    manager: ResourceManager

    def load_synthetic_dataset(self, dataset_name: str, synthesizer_name: str, epsilon: float, seed: int, size: int) -> Dataset:
        path = self.manager.resolver.resolve(
            "data", 
            name=dataset_name, 
            mode=DataMode.SYNTHETIC,
            synth_name=synthesizer_name,
            epsilon=epsilon,
            seed=seed,
            size=size
        )
        private_dataset = self.manager.load_dataset(dataset_name)
        df = pd.read_csv(path)
        return Dataset(
            name=f"{dataset_name}_syn",
            data=df,
            dcs=private_dataset.dcs,
            target=private_dataset.target,
            mappings=private_dataset.mappings
        )

    def load_marginal_set(self, dataset_name: str, noise_level: float) -> MarginalSet:
        path = self.manager.resolver.resolve(
            "marginal", 
            dataset_name=dataset_name, 
            noise_level=noise_level
        )
        with open(path, "r") as f:
            return MarginalSet.from_dict(json.load(f))

    def save_repaired_dataset(self, dataset: Dataset, repairer_name: str, synthesizer_name: str, epsilon: float, seed: int, size: int, alpha: float):
        path = self.manager.resolver.resolve(
            "data",
            name=dataset.name.replace("_syn", ""),
            mode=DataMode.REPAIRED,
            repairer_name=repairer_name,
            synth_name=synthesizer_name,
            epsilon=epsilon,
            seed=seed,
            size=size,
            alpha=alpha
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        dataset.data.to_csv(path, index=False)
        return path
