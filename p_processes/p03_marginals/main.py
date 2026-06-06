import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="config", config_name="default")
def main(cfg: DictConfig):
    """
    Declarative entry point for the marginals process.
    Uses Hydra to instantiate the Orchestrator triad.
    """
    worker = hydra.utils.instantiate(cfg)
    worker.run()

if __name__ == "__main__":
    main()
