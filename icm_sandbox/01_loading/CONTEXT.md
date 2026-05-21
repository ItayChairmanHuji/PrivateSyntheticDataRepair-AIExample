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
- `private_data.csv`: The cleaned private dataset.
- `metadata.json`: Dataset schema and statistics.
- `constraints.txt`: Denial constraints.

## Stage Rules
- Ensure data types are correctly mapped during loading.
- Metadata should include domain sizes for all categorical features.
