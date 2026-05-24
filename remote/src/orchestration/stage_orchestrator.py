from dataclasses import dataclass
from pathlib import Path
import logging
from remote.src.remote.pusher import Pusher
from remote.src.remote.puller import Puller
from remote.src.remote.deployer import Deployer

logger = logging.getLogger(__name__)

@dataclass
class StageOrchestrator:
    remote_host: str
    remote_dir: str
    mode: str
    blueprint: str = None
    exp_ids: list = None
    canary: bool = False
    paths: list = None

    def __post_init__(self):
        self.pusher = Pusher(remote_host=self.remote_host, remote_dir=self.remote_dir)
        self.puller = Puller(remote_host=self.remote_host, remote_dir=self.remote_dir)
        self.deployer = Deployer(remote_host=self.remote_host, remote_dir=self.remote_dir, pusher=self.pusher)

    def run(self):
        logger.info(f"Remote Utility Orchestrator started with mode: {self.mode}")
        
        if self.mode == "push":
            if self.paths:
                self.pusher.push_paths(self.paths)
            else:
                self.pusher.push()
        elif self.mode == "pull":
            if self.paths:
                self.puller.pull_paths(self.paths)
            elif self.blueprint:
                self.puller.pull(self.blueprint, exp_ids=self.exp_ids)
            else:
                logger.error("Error: 'blueprint' or 'paths' parameter is required for mode='pull'")
        elif self.mode == "deploy":
            if not self.blueprint:
                logger.error("Error: 'blueprint' parameter is required for mode='deploy'")
                return
            self.deployer.deploy(self.blueprint, canary_only=self.canary)
        else:
            logger.error(f"Unknown mode: {self.mode}. Supported modes: push, pull, deploy")
