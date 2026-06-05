# Utility: u_remote

## Purpose
Zero-friction synchronization between local environment and the cluster.

## Interface
- **`Pusher`**: Syncs code (git-based) and small configs.
- **`Puller`**: Retrieves results and metrics (scp-based).
- **`StateChecker`**: Verifies resource presence on the remote system.

## Usage
```bash
python -m u_utilities.u_remote.push
python -m u_utilities.u_remote.pull --experiment E001 --stats_only
```
