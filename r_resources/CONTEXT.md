# Resources (r_resources)

## Purpose
The `r_resources` directory is the single source of truth for all persistent state in the framework. It stores data, models, configurations, and results.

## Hierarchy Rules
All resources follow the **Parameter Identity** rule. Paths are calculated based on the parameters that define the resource.

### 1. Data (`r_data/`)
- `base/`: Raw ground-truth artifacts (CSV, DCs, Metadata).
- `private/`: Processed/Encoded ground-truth data created by `p01_loading`.
- `synthetic/`: Generated data, nested by `{synth}/{eps}/{seed}/{size}`.
- `repaired/`: Repaired data, nested by `{repairer}/{synth}/{eps}/{seed}/{size}/{alpha}`.

### 2. Models (`r_models/`)
- Trained model files (.pkl), nested by `{dataset}/{synth}/{eps}/{seed}`.

### 3. Configs (`r_configs/`)
- `base/`: Master registry of default parameters.
- `experiments/`: Hydra experiment files defining sweeps and compositions.

### 4. Results (`r_results/`)
- Evaluation metrics and JSON reports, grouped by `experiment_id` and `timestamp`.

## Management
- **Sync:** Managed via `u_remote` using SCP/rsync.
- **Access:** All read/write operations MUST go through the `ResourceManager` utility (`u_utilities.u_io`).
