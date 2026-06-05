from dataclasses import dataclass
from pathlib import Path
from u_utilities.u_io import ResourceManager, DataMode

@dataclass
class TrainingEngine:
    """Engine: Handles resource interaction for the training process."""
    manager: ResourceManager = None

    def __post_init__(self):
        if self.manager is None:
            self.manager = ResourceManager()

    def get_model_path(self, dataset_name: str, synth_name: str, epsilon: float, seed: int) -> Path:
        return self.manager.resolver.resolve(
            "model",
            dataset_name=dataset_name,
            synth_name=synth_name,
            epsilon=epsilon,
            seed=seed
        )

    def load_dataset(self, name: str):
        return self.manager.load_dataset(name, mode=DataMode.PRIVATE)

    def save_model(self, model: any, path: Path):
        self.manager.save_model(model, path=path)
