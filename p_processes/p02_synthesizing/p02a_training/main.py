import hydra
from omegaconf import DictConfig, OmegaConf
from p_processes.p02_synthesizing.p02a_training.src.worker import TrainingWorker

@hydra.main(version_base=None, config_path="../config", config_name="default")
def main(cfg: DictConfig):
    # Resilient accessor pattern
    if "training" in cfg:
        target_cfg = cfg.training
    elif "synthesizing" in cfg:
        target_cfg = cfg.synthesizing
    else:
        target_cfg = cfg
    
    # Instantiate the trainer (the Worker)
    trainer = hydra.utils.instantiate(target_cfg)
    
    # Instantiate and run the Orchestrator
    worker = TrainingWorker()
    model_path = worker.run(target_cfg, trainer)
        
    print(f"Success [p02a_training]: {target_cfg.dataset_name} -> {model_path}")

if __name__ == "__main__":
    main()
