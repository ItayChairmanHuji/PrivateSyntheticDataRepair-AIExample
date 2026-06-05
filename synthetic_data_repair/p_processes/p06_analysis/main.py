import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="../../r_resources/r_configs/base", config_name="analysis/default")
def main(cfg: DictConfig):
    """
    Declarative entry point for the analysis process.
    Uses Hydra to instantiate the Orchestrator triad.
    """
    target_cfg = cfg.orchestrator if "orchestrator" in cfg else cfg.analysis.orchestrator
    orchestrator = hydra.utils.instantiate(target_cfg)
    orchestrator.run()

if __name__ == "__main__":
    main()
