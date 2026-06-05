# Process: p02c_flow

## Overview
This process is a compound worker that sequentially executes `p02a_training` and `p02b_sampling`. It ensures that a model is trained and then sampled using consistent parameters.

## Responsibilities
- Sequential execution of training and sampling stages.
- Configuration consistency across the synthesis flow.

## Parameter Identity
- **Inputs**: Private dataset in `r_resources/r_data/`.
- **Outputs**: Trained model in `r_resources/r_models/` and synthetic dataset in `r_resources/r_data/`.

## Usage (CLI)
```bash
python -m p_processes.p02_synthesizing.p02c_flow.main dataset_name=adult100 engine=mst epsilon=1.0 seed=42
```

## Internal Architecture
Since this is a compound process, it does not define its own Engine/Worker triad. It delegates to the `p02a_training` and `p02b_sampling` processes.
