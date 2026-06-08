import logging
from pathlib import Path
from u_utilities.u_remote.src.path_resolver import RemotePathResolver
from u_utilities.u_remote.src.pusher import Pusher
from u_utilities.u_remote.src.puller import Puller
from u_utilities.u_remote.src.setup_worker import SetupWorker
from u_utilities.u_remote.src.data_pusher import DataPusher

logger = logging.getLogger(__name__)

class RemoteFacade:
    """
    Main entry point for remote operations.
    """
    def __init__(self, remote_host: str, remote_dir: str):
        self.resolver = RemotePathResolver(remote_host, remote_dir)
        self.pusher = Pusher(remote_host, remote_dir)
        self.puller = Puller(remote_host, remote_dir)
        self.setup_worker = SetupWorker(remote_host, remote_dir)
        self.data_pusher = DataPusher(remote_host, remote_dir)

    def push_codebase(self):
        root_dir = Path.cwd()
        self.pusher.push(root_dir)

    def push_resources(self):
        root_dir = Path.cwd()
        self.data_pusher.push_essential_resources(root_dir)

    def setup_environment(self):
        """
        Pushes requirements.txt and sets up the remote environment.
        """
        self.push_codebase()
        self.push_resources()
        self.setup_worker.run_setup()

    def pull_results(self, experiment_id: str):
        local_dir = Path.cwd() / "outputs" / experiment_id
        self.puller.pull_path(f"outputs/{experiment_id}", local_dir)
