# Stage 02 Execution Example: Generating Synthetic Data with AIM

This example shows how to take private data and generate a synthetic version using the AIM algorithm.

## 1. What you need to insert (Input)
- `private_data.csv` in `01_loading/output/`.
- A configuration file in `02_synthesizing/config/`.

**File: `config/aim_default.yaml`**
```yaml
_target_: src.synthesizing.aim_synthesizer.AimSynthesizer
epsilon: 1.0
delta: 1e-9
max_iters: 100
```

## 2. What I expect to see (Process)
The synthesizer trains on the private data (DP) and samples a new dataset.

**Command:**
```powershell
python 02_synthesizing/src/main.py --config aim_default.yaml --in 01_loading/output
```

## 3. What I will output (Output)
- `synthetic_data.csv`: The generated rows.
- `run_config.json`: Hyperparameters and seed used.
