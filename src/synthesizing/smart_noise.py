import random
import numpy as np
import torch
import pandas as pd
from snsynth import Synthesizer as SnSynthesizer
from src.entities.dataset import Dataset
from src.synthesizing.synthesizer import Synthesizer

class SmartNoiseSynthesizer(Synthesizer):
    """
    Integration with the SmartNoise (snsynth) library for Differential Privacy (DP) synthetic data generation.
    
    This synthesizer supports multiple DP algorithms provided by the SmartNoise ecosystem, 
    including MST, AIM, and PATECTGAN. It automatically handles basic data type inference 
    and ensures the output matches the project's Dataset structures.
    
    Attributes:
        engine (str): The name of the synthesis algorithm (e.g., "mst", "aim", "patectgan").
        epsilon (float): The privacy budget.
        seed (int): Random seed for reproducibility.
        kwargs (dict): Additional parameters passed directly to the underlying SmartNoise algorithm.
    """
    def __init__(self, engine: str, epsilon: float = 1.0, seed: int = 42, **kwargs):
        """
        Initializes the synthesizer with a specific engine and privacy parameters.
        
        Args:
            engine (str): Algorithm name.
            epsilon (float): Privacy budget (default: 1.0).
            seed (int): Random seed (default: 42).
            **kwargs: Extra arguments. Supports a nested 'kwargs' dictionary for compatibility.
        """
        self.engine = engine
        self.epsilon = epsilon
        self.seed = seed
        
        # Support both flattened kwargs and a nested 'kwargs' dictionary
        # Handle both dict and Hydra's DictConfig
        if 'kwargs' in kwargs:
            extra_args = kwargs.pop('kwargs')
            if extra_args and hasattr(extra_args, 'items'):
                kwargs.update(dict(extra_args))
        
        self.kwargs = kwargs

    def _set_seed(self):
        """Sets the seed for all relevant libraries to ensure reproducibility."""
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.seed)

    def synthesize(self, dataset: Dataset) -> Dataset:
        """
        Generates a synthetic version of the provided dataset.
        
        Args:
            dataset (Dataset): The source dataset to synthesize.
            
        Returns:
            Dataset: A new dataset object containing the synthetic data.
        """
        self._set_seed()
        
        # Filter out None and empty dicts to avoid TypeError in some SmartNoise engines
        filtered_kwargs = {k: v for k, v in self.kwargs.items() if v is not None}
        
        # If 'kwargs' still somehow exists and is empty, remove it
        if 'kwargs' in filtered_kwargs and not filtered_kwargs['kwargs']:
            filtered_kwargs.pop('kwargs')

        synth = SnSynthesizer.create(self.engine, epsilon=self.epsilon, **filtered_kwargs)
        synth.fit(dataset.data)
        synthetic_df = synth.sample(len(dataset.data))
        
        # Ensure it's a DataFrame (some engines might return numpy)
        if not isinstance(synthetic_df, pd.DataFrame):
            synthetic_df = pd.DataFrame(synthetic_df, columns=dataset.data.columns)

        return Dataset(
            name=f"{dataset.name}_{self.engine}",
            data=synthetic_df,
            dcs=dataset.dcs,
            target=dataset.target
        )
