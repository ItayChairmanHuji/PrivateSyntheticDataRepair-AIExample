# Stage 02: Synthesizing

## Purpose
Generate a synthetic version of the private dataset using various differentially private (DP) or non-DP algorithms.

## Contract
**Inputs (Layer 4 - `input/`):**
- All artifacts must be in a subdirectory named after the dataset (e.g., `input/adult100/`).
- `private_data.csv` and `metadata.json` from `01_loading/output/`.

**Reference Material (Layer 3 - `config/`):**
- Synthesizer configurations (e.g., `aim.yaml`, `mst.yaml`, `patectgan.yaml`).

**Process:**
- Train the generative model on the private data.
- Sample the model to create synthetic rows.

**Outputs (Layer 4 - `output/`):**
- All artifacts are saved in a subdirectory named after the dataset (e.g., `output/adult100/`).
- `synthetic_data.csv`: The generated synthetic dataset.
- `run_config.json`: Metadata about the synthesis run.

## Model Storage Format
To ensure consistency across the pipeline, trained models should be stored in the root `models/` directory using the following hierarchy:
`models/{dataset_name}/{algorithm}/{dataset_name}_{algorithm}_eps{epsilon}.pkl`

*Example:* `models/adult/aim/adult_aim_eps0.1.pkl`

## Stage Rules
- **Restricted Execution**: Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes to the data or code unless explicitly asked by the user.
- **Isolation**: Every dataset synthesis MUST have its own subdirectory in `output/`.
- **Integrity**: Always record the random seed and hyperparameters in a `run_config.json` in the output.

## Usage
To execute the synthesizing stage, run the following command from the project root:

```bash
# Full synthesis (Train + Sample) using default (MST)
python s02_synthesizing/src/main.py dataset_name=<dataset_name>

# Specific algorithm (e.g., AIM)
python s02_synthesizing/src/main.py --config-name aim dataset_name=<dataset_name>

# Training only (Saves model to models/)
python s02_synthesizing/src/main.py dataset_name=<dataset_name> mode=train

# Sampling only (Loads model from models/)
python s02_synthesizing/src/main.py --config-name model_loader dataset_name=<dataset_name> mode=sample
```

## Maintenance
To clear outputs:
```bash
# Clear all outputs
python s02_synthesizing/src/cli/clean.py

# Clear a specific dataset
python s02_synthesizing/src/cli/clean.py --dataset <dataset_name>
```
