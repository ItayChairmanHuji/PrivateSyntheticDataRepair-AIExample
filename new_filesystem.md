synthetic_data_repair/
├── mission_control/              # The "Brain" (Human Layer)
│   ├── journal/                  # Daily logs
│   └── experiments/              # Plain-language goals (E001.md)
│
├── r_resources/                  # The "State" (Deeply Nested by Parameters)
│   ├── r_data/
│   │   └── {dataset}/            # e.g., adult/
│   │       ├── private/          # Ground Truth
│   │       │   ├── data.csv
│   │       │   ├── metadata.json
│   │       │   └── dcs.txt
│   │       ├── synthetic/
│   │       │   └── {synth}/      # e.g., aim/
│   │       │       └── {eps}/    # e.g., 0.1/
│   │       │           └── {seed}/
│   │       │               └── {size}/
│   │       │                   └── data.csv
│   │       └── repaired/
│   │           └── {repairer}/   # e.g., vanilla_vc/
│   │               └── {synth}/
│   │                   └── {eps}/
│   │                       └── {seed}/
│   │                           └── {size}/
│   │                               └── {alpha}/
│   │                                   └── data.csv
│   ├── r_models/
│   │   └── {dataset}/
│   │       └── {synth}/
│   │           └── {eps}/
│   │               └── {seed}.pkl
│   ├── r_marginals/
│   │   └── {dataset}/
│   │       └── {noise_level}/
│   │           └── marginals.json
│   ├── r_results/
│   │   └── {experiment_id}/      # e.g., E001/
│   │       └── {timestamp}/      # Unique sweep run
│   │           ├── sweep_summary.csv
│   │           └── jobs/
│   │               └── {params_hash_or_id}/
│   │                   └── metrics.json
│   ├── r_configs/                # Hydra Store
│   │   ├── base/                 # (dataset/, synth/, repairer/, loading/)
│   │   └── experiments/          # E001.yaml, E002.yaml
│   └── r_analysis/
│       ├── notebooks/
│       └── figures/
│
├── p_processes/                  # The "Verbs" (Granular & Standardized)
│   # Internal Structure:
│   # p_name/
│   # ├── main.py                 # @hydra.main entry point
│   │ ├── src/                    # Internal logic (not for export)
│   │ ├── tests/                  # Process-specific unit tests
│   │ └── README.md               # Local usage & parameter docs
│   │
│   ├── p01_loading/
│   ├── p02a_training/
│   ├── p02b_sampling/
│   ├── p03_marginals/
│   ├── p04_repairing/
│   ├── p05_evaluating/
│   └── p06_analysis/
│
├── u_utilities/                  # The "Tools" (Atomic & Exportable)
│   # Internal Structure:
│   # u_name/
│   # ├── __init__.py             # Public API
│   │ ├── main.py                 # CLI for standalone use
│   │ ├── src/                    # Shared logic
│   │ ├── tests/                  # Utility unit tests
│   │ └── README.md               # API documentation
│   │
│   ├── u_shared/                 # Entities (Dataset, DC, Marginal)
│   ├── u_violation_finder/
│   ├── u_remote/                 # Zero-Friction Sync
│   ├── u_mission_control/        # Hydra-Config generator helpers
│   ├── u_io/                     # THE LINKER: (Config -> Path)
│   └── u_visualizer/             # Plotting & Tables
│
└── REPOSITORY_RULES.md
    # 1. Parameter Identity (The Core Logic):
    #    - Path resolution is purely functional: f(params) -> path.
    #    - No "magic" strings in code; all paths must come from u_io.
    # 2. Granularity & Reuse:
    #    - If logic is used by >1 process, move it to u_utilities.
    # 3. Hydra-First:
    #    - CLI overrides must be supported for every parameter in the resource hierarchy.








