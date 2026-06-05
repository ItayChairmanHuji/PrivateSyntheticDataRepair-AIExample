import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="config", config_name="adult100")
def main(cfg: DictConfig):
    """
    Declarative entry point for the loading process.
    Uses Hydra to instantiate the Orchestrator triad.
    """
    # The worker is the primary facade
    # Handle potential nesting by Hydra
    target_cfg = cfg.worker if "worker" in cfg else cfg.loading.worker
    worker = hydra.utils.instantiate(target_cfg)
    worker.run()

if __name__ == "__main__":
    main()
