import dill
from pathlib import Path
from snsynth import Synthesizer as SnSynthesizer

from shared.entities.dataset import Dataset
from s02_synthesizing.src.components.smart_noise import SmartNoiseSynthesizer

class SmartNoiseModelTrainer(SmartNoiseSynthesizer):
    """
    Synthesizer that trains a SmartNoise model, saves it to disk, 
    and generates synthetic data.
    """
    def __init__(self, engine: str, epsilon: float = 1.0, seed: int = 42, 
                 save_path: str = "models", **kwargs):
        super().__init__(engine, epsilon, seed, **kwargs)
        self.save_path = Path(save_path)

    def _get_model_full_path(self, dataset_name: str) -> Path:
        """Constructs the full path for the model following the project hierarchy."""
        return self.save_path / dataset_name / self.engine / f"{dataset_name}_{self.engine}_eps{self.epsilon}.pkl"

    def fit_and_save(self, dataset: Dataset) -> any:
        """
        Trains the model and saves it to disk.
        """
        self._set_seed()
        
        filtered_kwargs = {k: v for k, v in self.kwargs.items() if v is not None}
        if 'kwargs' in filtered_kwargs and not filtered_kwargs['kwargs']:
            filtered_kwargs.pop('kwargs')

        # Separate kwargs for create and fit.
        fit_params = ["categorical_columns", "ordinal_columns", "continuous_columns"]
        create_kwargs = {k: v for k, v in filtered_kwargs.items() if k not in fit_params}
        fit_kwargs = {k: v for k, v in filtered_kwargs.items() if k in fit_params}

        print(f"Training {self.engine} on {dataset.name} with epsilon={self.epsilon}...")
        synth = SnSynthesizer.create(self.engine, epsilon=self.epsilon, **create_kwargs)
        
        # Simple fit logic
        synth.fit(dataset.data, **fit_kwargs)

        full_path = self._get_model_full_path(dataset.name)
        full_path.parent.mkdir(exist_ok=True, parents=True)
        
        print(f"Saving model to {full_path}...")
        with open(full_path, "wb") as f:
            dill.dump(synth, f)
        
        return synth

    def sample(self, dataset: Dataset) -> Dataset:
        """
        Loads the trained model from disk and generates synthetic data.
        """
        full_path = self._get_model_full_path(dataset.name)
        if not full_path.exists():
            raise FileNotFoundError(f"Model file not found: {full_path}. Did you run with mode=train?")
            
        print(f"Loading model for sampling from {full_path}...")
        with open(full_path, "rb") as f:
            model = dill.load(f)
            
        return super().sample(model, dataset)

    def synthesize(self, dataset: Dataset) -> Dataset:
        """
        Trains the model, saves it, and generates synthetic data.
        """
        model = self.fit_and_save(dataset)
        return super().sample(model, dataset)
