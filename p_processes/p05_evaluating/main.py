import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="config", config_name="default")
def main(cfg: DictConfig):
    """
    Declarative entry point for the evaluating process.
    Uses Hydra to instantiate the Orchestrator triad.
    """
    target_cfg = cfg.worker if "worker" in cfg else cfg.evaluating.worker
    worker = hydra.utils.instantiate(target_cfg)
    worker.run()

if __name__ == "__main__":
    main()
