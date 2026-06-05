from dataclasses import dataclass
from u_utilities.u_shared import Dataset

@dataclass
class TrainingCore:
    """Logic: Performs the training core."""
    def train(self, trainer: any, dataset: Dataset) -> any:
        """Trains the model using the provided trainer and dataset."""
        return trainer.train(dataset)
