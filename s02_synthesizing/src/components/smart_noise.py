import random
import numpy as np
import torch
import pandas as pd
from snsynth import Synthesizer as SnSynthesizer
from shared.entities.dataset import Dataset
from s02_synthesizing.src.components.synthesizer import Synthesizer

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
        
        # Prevent pipeline-level parameters from being passed to SmartNoise engines
        for key in ['mode', 'save_path', 'dataset_name', 'sample_size', 'model_path', 'size', 'engine']:
            kwargs.pop(key, None)
        
        self.kwargs = kwargs

    def _set_seed(self):
        """Sets the seed for all relevant libraries to ensure reproducibility."""
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.seed)

    def sample(self, model, dataset: Dataset) -> Dataset:
        """
        Generates synthetic data from a pre-trained model.
        
        Args:
            model: The pre-trained SmartNoise model.
            dataset (Dataset): Reference dataset for metadata and size.
            
        Returns:
            Dataset: Synthetic dataset.
        """
        self._set_seed()
        
        # Pass seed directly to sample() for engines that support it
        try:
            synthetic_df = model.sample(len(dataset.data), seed=self.seed)
        except TypeError:
            synthetic_df = model.sample(len(dataset.data))
        
        # Ensure it's a DataFrame (some engines might return numpy)
        if not isinstance(synthetic_df, pd.DataFrame):
            synthetic_df = pd.DataFrame(synthetic_df, columns=dataset.data.columns)

        return Dataset(
            name=f"{dataset.name}_{self.engine}_sampled",
            data=synthetic_df,
            dcs=dataset.dcs,
            target=dataset.target,
            mappings=dataset.mappings
        )

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
        
        # Use mappings to identify categorical columns, others are continuous
        cat_cols = list(dataset.mappings.keys()) if dataset.mappings else []
        cont_cols = [col for col in dataset.data.columns if col not in cat_cols]
        
        # Fit the synthesizer
        if self.engine.lower() == 'aim':
            # AIM is very picky about column types
            synth.fit(dataset.data, categorical_columns=cat_cols, continuous_columns=cont_cols, **self.kwargs)
        else:
            # Other engines like MST might prefer just categorical_columns
            if cat_cols:
                synth.fit(dataset.data, categorical_columns=cat_cols, **self.kwargs)
            else:
                synth.fit(dataset.data, **self.kwargs)

        # Pass seed directly to sample() for engines that support it
        try:
            synthetic_df = synth.sample(len(dataset.data), seed=self.seed)
        except TypeError:
            synthetic_df = synth.sample(len(dataset.data))
        
        # Ensure it's a DataFrame (some engines might return numpy)
        if not isinstance(synthetic_df, pd.DataFrame):
            synthetic_df = pd.DataFrame(synthetic_df, columns=dataset.data.columns)

        return Dataset(
            name=f"{dataset.name}_{self.engine}",
            data=synthetic_df,
            dcs=dataset.dcs,
            target=dataset.target,
            mappings=dataset.mappings
        )

