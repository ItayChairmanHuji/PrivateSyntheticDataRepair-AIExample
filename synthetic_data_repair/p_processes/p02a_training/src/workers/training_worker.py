from dataclasses import dataclass
import hydra
from omegaconf import DictConfig
from u_utilities.u_shared import Dataset

@dataclass
class TrainingWorker:
    """
    Atomic worker that performs the training logic.
    """
    
    def train(self, trainer: any, dataset: Dataset) -> any:
        """
        Trains the model using the provided trainer and dataset.
        """
        return trainer.train(dataset)
