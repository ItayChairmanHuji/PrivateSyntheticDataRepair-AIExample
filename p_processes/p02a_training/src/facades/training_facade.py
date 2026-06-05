from dataclasses import dataclass
from ..engines.training_engine import TrainingEngine
from ..workers.training_worker import TrainingWorker

@dataclass
class TrainingFacade:
    """
    Facade orchestrator that coordinates the Engine and Workers.
    """
    engine: TrainingEngine = None
    worker: TrainingWorker = None

    def __post_init__(self):
        self.engine = self.engine or TrainingEngine()
        self.worker = self.worker or TrainingWorker()

    def run(self, cfg: any, trainer: any):
        # 1. Load data
        dataset = self.engine.load_dataset(cfg.dataset_name)
        
        # 2. Train model
        model = self.worker.train(trainer, dataset)
        
        # 3. Resolve path and save
        model_path = self.engine.get_model_path(
            dataset_name=cfg.dataset_name,
            synth_name=cfg.engine, # Config uses 'engine' for synthesizer name
            epsilon=cfg.epsilon,
            seed=cfg.seed
        )
        self.engine.save_model(model, model_path)
        
        return model_path
