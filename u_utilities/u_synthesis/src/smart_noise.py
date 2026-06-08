import random
import numpy as np
import torch
import pandas as pd
from snsynth import Synthesizer as SnSynthesizer
from u_utilities.u_shared import Dataset
from .synthesizer import Synthesizer, ModelTrainer, ModelSampler

class SmartNoiseSynthesizer(Synthesizer, ModelTrainer, ModelSampler):
    """
    Integration with the SmartNoise (snsynth) library.
    """
    def __init__(self, engine: str, epsilon: float = 1.0, seed: int = 42, **kwargs):
        self.engine = engine
        self.epsilon = epsilon
        self.seed = seed
        self.kwargs = self._clean_kwargs(kwargs)

    def _clean_kwargs(self, kwargs):
        if 'kwargs' in kwargs:
            extra_args = kwargs.pop('kwargs')
            if extra_args and hasattr(extra_args, 'items'):
                kwargs.update(dict(extra_args))
        for key in ['mode', 'dataset_name', 'save_path', 'sample_size', 'model_path', 'size', 'synthesizer_name']:
            kwargs.pop(key, None)
        return {k: v for k, v in kwargs.items() if v is not None}

    def _set_seed(self, seed: int):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

    def train(self, dataset: Dataset) -> any:
        self._set_seed(self.seed)
        fit_params = ["categorical_columns", "ordinal_columns", "continuous_columns"]
        create_kwargs = {k: v for k, v in self.kwargs.items() if k not in fit_params}
        fit_kwargs = {k: v for k, v in self.kwargs.items() if k in fit_params}
        if "categorical_columns" not in fit_kwargs:
            fit_kwargs["categorical_columns"] = list(dataset.data.columns)

        print(f"Training {self.engine} (epsilon={self.epsilon})...")
        synth = SnSynthesizer.create(self.engine, epsilon=self.epsilon, **create_kwargs)
        synth.fit(dataset.data, **fit_kwargs)
        return synth

    def sample(self, model: any, dataset: Dataset, size: int) -> Dataset:
        self._set_seed(self.seed)
        try:
            synthetic_df = model.sample(size, seed=self.seed)
        except TypeError:
            synthetic_df = model.sample(size)
        
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
        model = self.train(dataset)
        return self.sample(model, dataset, len(dataset.data))
