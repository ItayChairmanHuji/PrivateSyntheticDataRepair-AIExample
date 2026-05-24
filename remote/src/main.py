import hydra
from omegaconf import DictConfig
from remote.src.orchestration.stage_orchestrator import StageOrchestrator
import logging

logger = logging.getLogger(__name__)

@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig):
    orchestrator = StageOrchestrator(
        remote_host=cfg.remote_host,
        remote_dir=cfg.remote_dir,
        mode=cfg.mode,
        blueprint=cfg.get("blueprint"),
        exp_ids=cfg.get("exp_ids"),
        canary=cfg.get("canary", False),
        paths=cfg.get("paths")
    )
    orchestrator.run()

if __name__ == "__main__":
    main()
