import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="../../r_resources/r_configs/base", config_name="loading/adult100")
def main(cfg: DictConfig):
    """
    Declarative entry point for the loading process.
    Uses Hydra to instantiate the Orchestrator triad.
    """
    # The orchestrator is the primary facade
    # Handle potential nesting by Hydra
    target_cfg = cfg.orchestrator if "orchestrator" in cfg else cfg.loading.orchestrator
    orchestrator = hydra.utils.instantiate(target_cfg)
    orchestrator.run()

if __name__ == "__main__":
    main()
