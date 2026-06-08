from pathlib import Path

class RemotePathResolver:
    """
    Handles remote path resolution and environment configuration.
    """
    def __init__(self, remote_host: str, remote_dir: str):
        self.remote_host = remote_host
        self.remote_dir = Path(remote_dir).as_posix()

    def get_remote_path(self, relative_path: str) -> str:
        return f"{self.remote_dir}/{relative_path}"

    def get_ssh_target(self, relative_path: str = "") -> str:
        if not relative_path:
            return f"{self.remote_host}:{self.remote_dir}"
        return f"{self.remote_host}:{self.get_remote_path(relative_path)}"
