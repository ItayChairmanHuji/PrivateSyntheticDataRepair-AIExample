import hydra
from omegaconf import DictConfig
import sys
from pathlib import Path

# Root in path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

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
        paths=cfg.get("paths"),
        stats_only=cfg.get("stats_only", False)
    )
    orchestrator.run()

if __name__ == "__main__":
    main()
