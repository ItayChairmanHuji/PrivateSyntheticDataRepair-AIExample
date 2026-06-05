import hydra
from omegaconf import DictConfig
from p_processes.p02a_training.src.facades.training_facade import TrainingFacade

@hydra.main(version_base=None, config_path="../../r_resources/r_configs/base", config_name="synthesizing/model_trainer")
def main(cfg: DictConfig):
    # Resilient accessor pattern
    target_cfg = cfg.training if "training" in cfg else cfg
    
    # Instantiate the trainer (the Worker)
    trainer = hydra.utils.instantiate(target_cfg)
    
    # Instantiate and run the Facade
    facade = TrainingFacade()
    model_path = facade.run(target_cfg, trainer)
        
    print(f"Success [p02a_training]: {target_cfg.dataset_name} -> {model_path}")

if __name__ == "__main__":
    main()
