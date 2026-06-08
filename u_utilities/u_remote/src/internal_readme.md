# Remote Utility Implementation Blueprint

## Theory of Operation
The `u_remote` utility provides a high-level API for synchronizing a local development environment with a remote cluster. It handles code deployment (push) and result retrieval (pull) while abstracting the underlying `ssh`, `scp`, and `zip` commands.

## Architecture
- **RemotePathResolver (Engine)**: Centralizes logic for converting local relative paths to remote absolute paths and SSH targets.
- **Pusher (Worker)**: Handles the complexity of zipping the codebase, excluding unnecessary files (e.g., `old/`, `.venv/`), and extracting it on the remote host.
- **Puller (Worker)**: Manages remote-to-local synchronization, automatically zipping remote directories for efficient transfer.
- **SetupWorker (Worker)**: Handles remote environment creation (virtualenv) and dependency installation.
- **RemoteFacade (Facade)**: Orchestrates the engine and workers to provide a simple public API.

## Implementation Details
### Remote Setup (Setup)
1.  **Sync**: Pushes the latest codebase (including `requirements.txt`).
2.  **Environment**: Creates a `.venv` on the remote if it doesn't exist.
3.  **Dependencies**: Installs/updates packages from `requirements.txt`.

### Codebase Synchronization (Push)
1.  **Exclusion**: The `Pusher` maintains a strict set of default excludes, including `old/`, to ensure only relevant research code is uploaded.
2.  **Compression**: The entire project (minus excludes) is zipped locally.
3.  **Transfer**: The zip archive is uploaded via `scp`.
4.  **Extraction**: The archive is extracted on the remote host using `unzip`, and the temporary zip file is removed.

### Result Retrieval (Pull)
1.  **Directory Detection**: The `Puller` checks if the requested remote path is a directory.
2.  **Remote Zipping**: If it's a directory, it is zipped on the remote host to minimize `scp` overhead.
3.  **Local Extraction**: The zip is pulled and extracted to the target local directory.

## Contract
### Inputs
- `remote_host`: SSH hostname of the cluster.
- `remote_dir`: Root directory for the project on the cluster.
- `mode`: Operation mode (`push` or `pull`).

### Side Effects
- Modifies files on the remote host (`push`).
- Creates/updates files in the local `outputs/` directory (`pull`).
