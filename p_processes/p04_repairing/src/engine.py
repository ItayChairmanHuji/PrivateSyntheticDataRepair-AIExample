import json
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager, DataMode
from u_utilities.u_shared import Dataset, MarginalSet

@dataclass
class RepairingEngine:
    manager: ResourceManager

    def load_synthetic_dataset(self, d_name: str, s_name: str, eps: float, seed: int, size: int) -> Dataset:
        path = self._resolve_synth_path(d_name, s_name, eps, seed, size)
        private = self.manager.load_dataset(d_name)
        return Dataset(
            name=f"{d_name}_syn",
            data=pd.read_csv(path),
            dcs=private.dcs,
            target=private.target,
            mappings=private.mappings
        )

    def _resolve_synth_path(self, name: str, s_name: str, eps: float, seed: int, size: int):
        return self.manager.resolver.resolve(
            "data", name=name, mode=DataMode.SYNTHETIC,
            synth_name=s_name, epsilon=eps, seed=seed, size=size
        )

    def load_marginal_set(self, dataset_name: str, noise_level: float) -> MarginalSet:
        path = self.manager.resolver.resolve("marginal", dataset_name=dataset_name, noise_level=noise_level)
        with open(path, "r") as f:
            return MarginalSet.from_dict(json.load(f))

    def save_repaired_dataset(self, dataset: Dataset, r_name: str, s_name: str, eps: float, seed: int, size: int, noise_level: Any, alpha: float):
        path = self._resolve_repaired_path(dataset.name, r_name, s_name, eps, seed, size, noise_level, alpha)
        path.parent.mkdir(parents=True, exist_ok=True)
        dataset.data.to_csv(path, index=False)
        return path

    def _resolve_repaired_path(self, name: str, r_name: str, s_name: str, eps: float, seed: int, size: int, noise_level: Any, alpha: float):
        return self.manager.resolver.resolve(
            "data", name=name.replace("_syn", ""), mode=DataMode.REPAIRED,
            repairer_name=r_name, synth_name=s_name, epsilon=eps, seed=seed, size=size, noise_level=noise_level, alpha=alpha
        )
