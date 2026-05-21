import hydra
from omegaconf import DictConfig, OmegaConf
from remote.src.components.pusher import Pusher
from remote.src.components.puller import Puller
from remote.src.components.deployer import Deployer
import logging

logger = logging.getLogger(__name__)

@hydra.main(version_base=None, config_path="../config", config_name="config")
def main(cfg: DictConfig):
    logger.info(f"Remote Utility started with mode: {cfg.mode}")
    
    pusher = Pusher(remote_host=cfg.remote_host, remote_dir=cfg.remote_dir)
    puller = Puller(remote_host=cfg.remote_host, remote_dir=cfg.remote_dir)
    deployer = Deployer(remote_host=cfg.remote_host, remote_dir=cfg.remote_dir, pusher=pusher)

    if cfg.mode == "push":
        pusher.push()
    elif cfg.mode == "pull":
        if not cfg.blueprint:
            logger.error("Error: 'blueprint' parameter is required for mode='pull'")
            return
        puller.pull(cfg.blueprint)
    elif cfg.mode == "deploy":
        if not cfg.blueprint:
            logger.error("Error: 'blueprint' parameter is required for mode='deploy'")
            return
        deployer.deploy(cfg.blueprint, canary_only=cfg.canary)
    else:
        logger.error(f"Unknown mode: {cfg.mode}. Supported modes: push, pull, deploy")

if __name__ == "__main__":
    main()
