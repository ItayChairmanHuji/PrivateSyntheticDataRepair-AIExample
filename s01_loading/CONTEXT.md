# Stage 01: Loading

## Purpose
Responsible for reading private datasets, metadata, and denial constraints.

## Contract
**Inputs (Layer 3 - `config/`):**
- Data loader configurations (e.g., `adult.yaml`, `census.yaml`).
- Raw data files in the global `data/` directory.

**Process:**
- Instantiate the appropriate `DataLoader`.
- Clean and preprocess the data into the internal `Dataset` entity.

**Outputs (Layer 4 - `output/`):**
- All artifacts are saved in a subdirectory named after the dataset (e.g., `output/adult100/`).
- `private_data.csv`: The cleaned private dataset.
- `metadata.json`: Dataset schema and statistics.
- `constraints.txt`: Denial constraints.

## Stage Rules
- **Restricted Execution**: Only commands documented in the [Usage](#usage) section are allowed. Do NOT apply any manual changes to the data or code unless explicitly asked by the user.
- **Isolation**: Every dataset load MUST have its own subdirectory in `output/`.
- **Integrity**: Metadata and constraints MUST match the cleaned data.

## Usage
To execute the loading stage, run the following command from the project root:

```bash
# List available datasets
python s01_loading/src/cli/list_datasets.py

# Default (adult100)
python s01_loading/src/main.py

# Specific dataset
python s01_loading/src/main.py --config-name <dataset_name>
```

## Maintenance
To clear outputs:
```bash
# Clear all outputs
python s01_loading/src/cli/clean.py

# Clear a specific dataset
python s01_loading/src/cli/clean.py --dataset <dataset_name>
```
