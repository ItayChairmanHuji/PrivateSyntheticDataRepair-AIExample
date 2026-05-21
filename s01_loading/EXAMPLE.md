# Stage 01 Execution Example: Loading Census Data

This example demonstrates how to load a raw dataset into the standardized `Dataset` entity.

## 1. What you need to insert (Input)
A configuration file in `01_loading/config/`.

**File: `config/census_loader.yaml`**
```yaml
_target_: src.loading.census_loader.CensusLoader
data_path: data/census/data.csv
metadata_path: data/census/metadata.json
target_column: income
```

## 2. What I expect to see (Process)
The loader script reads the config, parses the CSV, and ensures it matches the metadata.

**Command:**
```powershell
python 01_loading/src/main.py --config census_loader.yaml
```

## 3. What I will output (Output)
Standardized artifacts in `01_loading/output/`.
- `private_data.csv`: Cleaned and typed data.
- `metadata.json`: Domain sizes and column types.
- `constraints.txt`: Denial constraints (if any).
