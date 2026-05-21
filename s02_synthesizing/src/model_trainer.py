import dill
import pandas as pd
from pathlib import Path
from typing import Optional
from snsynth import Synthesizer as SnSynthesizer

from shared.entities.dataset import Dataset
from s02_synthesizing.src.smart_noise import SmartNoiseSynthesizer

class SmartNoiseModelTrainer(SmartNoiseSynthesizer):
    """
    Synthesizer that trains a SmartNoise model, saves it to disk, 
    and generates synthetic data.
    """
    def __init__(self, engine: str, epsilon: float = 1.0, seed: int = 42, 
                 save_path: str = "models", **kwargs):
        """
        Args:
            engine (str): Algorithm name (e.g., "mst", "aim").
            epsilon (float): Privacy budget.
            seed (int): Random seed.
            save_path (str): Directory where the trained model will be saved.
            **kwargs: Extra arguments for the SmartNoise algorithm.
        """
        super().__init__(engine, epsilon, seed, **kwargs)
        self.save_path = Path(save_path)

    def fit_and_save(self, dataset: Dataset):
        """
        Trains the model and saves it to disk, without generating synthetic data.
        """
        self._set_seed()
        
        filtered_kwargs = {k: v for k, v in self.kwargs.items() if v is not None}
        if 'kwargs' in filtered_kwargs and not filtered_kwargs['kwargs']:
            filtered_kwargs.pop('kwargs')

        print(f"Training {self.engine} on {dataset.name} with epsilon={self.epsilon}...")
        synth = SnSynthesizer.create(self.engine, epsilon=self.epsilon, **filtered_kwargs)
        synth.fit(dataset.data, categorical_columns=dataset.data.columns.tolist())

        self.save_path.mkdir(exist_ok=True, parents=True)
        model_filename = f"{dataset.name}_{self.engine}_eps{self.epsilon}.pkl"
        full_path = self.save_path / model_filename
        
        print(f"Saving model to {full_path}...")
        with open(full_path, "wb") as f:
            dill.dump(synth, f)

    def synthesize(self, dataset: Dataset) -> Dataset:
        """
        Trains the model, saves it, and generates synthetic data.
        
        Args:
            dataset (Dataset): The source dataset to train on.
            
        Returns:
            Dataset: A new dataset object containing the synthetic data.
        """
        self._set_seed()
        
        # Filter out None and empty dicts
        filtered_kwargs = {k: v for k, v in self.kwargs.items() if v is not None}
        if 'kwargs' in filtered_kwargs and not filtered_kwargs['kwargs']:
            filtered_kwargs.pop('kwargs')

        print(f"Training {self.engine} on {dataset.name} with epsilon={self.epsilon}...")
        synth = SnSynthesizer.create(self.engine, epsilon=self.epsilon, **filtered_kwargs)
        
        # Training (following reference script by passing categorical columns)
        synth.fit(dataset.data, categorical_columns=dataset.data.columns.tolist())

        # Save model
        self.save_path.mkdir(exist_ok=True, parents=True)
        model_filename = f"{dataset.name}_{self.engine}_eps{self.epsilon}.pkl"
        full_path = self.save_path / model_filename
        
        print(f"Saving model to {full_path}...")
        with open(full_path, "wb") as f:
            dill.dump(synth, f)

        # Generate synthetic data
        try:
            synthetic_df = synth.sample(len(dataset.data), seed=self.seed)
        except TypeError:
            synthetic_df = synth.sample(len(dataset.data))
        
        # Ensure it's a DataFrame
        if not isinstance(synthetic_df, pd.DataFrame):
            synthetic_df = pd.DataFrame(synthetic_df, columns=dataset.data.columns)

        return Dataset(
            name=f"{dataset.name}_{self.engine}_trained",
            data=synthetic_df,
            dcs=dataset.dcs,
            target=dataset.target,
            mappings=dataset.mappings  # Preserve mappings
        )

