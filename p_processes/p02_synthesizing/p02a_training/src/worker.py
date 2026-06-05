from dataclasses import dataclass
from .engine import TrainingEngine
from .core.training_core import TrainingCore

@dataclass
class TrainingWorker:
    """Orchestrator: Coordinates the Engine and Logic for the training process."""
    engine: TrainingEngine = None
    core: TrainingCore = None

    def __post_init__(self):
        self.engine = self.engine or TrainingEngine()
        self.core = self.core or TrainingCore()

    def run(self, cfg: any, trainer: any):
        # 1. Use the Engine to load the resource
        dataset = self.engine.load_dataset(cfg.dataset_name)
        
        # 2. Use Logic to perform the training
        model = self.core.train(trainer, dataset)
        
        # 3. Use the Engine to resolve path and save
        model_path = self.engine.get_model_path(
            dataset_name=cfg.dataset_name,
            synth_name=cfg.engine, # Config uses 'engine' for synthesizer name
            epsilon=cfg.epsilon,
            seed=cfg.seed
        )
        self.engine.save_model(model, model_path)
        
        return model_path
