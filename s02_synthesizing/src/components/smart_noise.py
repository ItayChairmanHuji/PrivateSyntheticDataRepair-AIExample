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
    """
    def __init__(self, engine: str, epsilon: float = 1.0, seed: int = 42, **kwargs):
        self.engine = engine
        self.epsilon = epsilon
        self.seed = seed
        
        # Support both flattened kwargs and a nested 'kwargs' dictionary
        if 'kwargs' in kwargs:
            extra_args = kwargs.pop('kwargs')
            if extra_args and hasattr(extra_args, 'items'):
                kwargs.update(dict(extra_args))
        
        # Remove pipeline-level parameters that might be in kwargs from Hydra
        for key in ['mode', 'dataset_name', 'save_path', 'sample_size', 'model_path', 'size']:
            kwargs.pop(key, None)
            
        self.kwargs = kwargs

    def _set_seed(self):
        random.seed(self.seed)
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.seed)

    def synthesize(self, dataset: Dataset) -> Dataset:
        self._set_seed()
        
        # Filter out None and empty dicts to avoid TypeError in some SmartNoise engines
        filtered_kwargs = {k: v for k, v in self.kwargs.items() if v is not None}
        
        # Instantiate and fit using the original simple logic
        synth = SnSynthesizer.create(self.engine, epsilon=self.epsilon, **filtered_kwargs)
        
        print(f"Synthesizing using {self.engine} (epsilon={self.epsilon})...")
        synth.fit(dataset.data)

        # Pass seed directly to sample() for engines that support it
        try:
            synthetic_df = synth.sample(len(dataset.data), seed=self.seed)
        except TypeError:
            synthetic_df = synth.sample(len(dataset.data))
        
        # Ensure it's a DataFrame
        if not isinstance(synthetic_df, pd.DataFrame):
            synthetic_df = pd.DataFrame(synthetic_df, columns=dataset.data.columns)

        return Dataset(
            name=f"{dataset.name}_{self.engine}",
            data=synthetic_df,
            dcs=dataset.dcs,
            target=dataset.target,
            mappings=dataset.mappings
        )
