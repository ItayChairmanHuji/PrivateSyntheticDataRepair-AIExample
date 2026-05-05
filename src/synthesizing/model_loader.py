import dill
import pandas as pd
import numpy as np
import torch
import random
from typing import Optional
from pathlib import Path

from src.entities.dataset import Dataset
from src.synthesizing.synthesizer import Synthesizer

class SmartNoiseModelLoader(Synthesizer):
    """
    Synthesizer that loads a pre-trained SmartNoise model from a file 
    and generates synthetic data.
    """
    def __init__(self, model_path: str, size: Optional[int] = None, seed: int = 42):
        """
        Args:
            model_path (str): Path to the saved .pkl model.
            size (int, optional): Number of rows to generate. If None, uses original dataset size.
            seed (int): Random seed for reproducibility.
        """
        self.model_path = Path(model_path)
        self.size = size
        self.seed = seed
        self._model = None

    def _set_seed(self):
        """
        Sets the seed for all relevant libraries to ensure reproducibility.
        """
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.seed)
        # Some SmartNoise engines might use their own generators, 
        # but most rely on these standard ones or pass seed to sample() if supported.

    def _load_model(self):
        if self._model is None:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            with open(self.model_path, "rb") as f:
                self._model = dill.load(f)

    def synthesize(self, dataset: Dataset) -> Dataset:
        """
        Generates synthetic data using the loaded model.
        Note: The 'dataset' argument is primarily used to preserve metadata (DCs, mappings).
        
        Args:
            dataset (Dataset): The reference dataset (used for metadata).
            
        Returns:
            Dataset: A new dataset object containing the synthetic data.
        """
        self._load_model()
        self._set_seed()
        
        gen_size = self.size if self.size is not None else len(dataset.data)
        
        print(f"Generating {gen_size} rows using model from {self.model_path} (seed={self.seed})...")
        
        # SmartNoise sample() usually supports a 'seed' argument in some versions, 
        # but we've already set the global seeds which should cover it.
        synthetic_df = self._model.sample(gen_size)
        
        # Ensure it's a DataFrame
        if not isinstance(synthetic_df, pd.DataFrame):
            synthetic_df = pd.DataFrame(synthetic_df, columns=dataset.data.columns)

        return Dataset(
            name=f"{dataset.name}_loaded_{self.model_path.stem}",
            data=synthetic_df,
            dcs=dataset.dcs,
            target=dataset.target,
            mappings=dataset.mappings  # Preserve encodings/mappings
        )
