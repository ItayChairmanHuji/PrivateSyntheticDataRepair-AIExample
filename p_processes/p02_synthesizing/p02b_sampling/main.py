import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="../config", config_name="sampling_flow")
def main(cfg: DictConfig):
    """
    Declarative entry point for the sampling process.
    Uses Hydra to instantiate the Orchestrator triad.
    """
    if "worker" in cfg:
        target_cfg = cfg.worker
    elif "sampling" in cfg and "worker" in cfg.sampling:
        target_cfg = cfg.sampling.worker
    elif "_target_" in cfg:
        target_cfg = cfg
    else:
        # Fallback if nested
        keys = list(cfg.keys())
        if len(keys) == 1 and isinstance(cfg[keys[0]], DictConfig) and "_target_" in cfg[keys[0]]:
            target_cfg = cfg[keys[0]]
        else:
            target_cfg = cfg

    worker = hydra.utils.instantiate(target_cfg)
    worker.run()

if __name__ == "__main__":
    main()
