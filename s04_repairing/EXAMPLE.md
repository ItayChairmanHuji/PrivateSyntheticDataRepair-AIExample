# Stage 04 Execution Example: Repairing with Weighted VC

This example shows the core repair process.

## 1. What you need to insert (Input)
- `synthetic_data.csv` and `marginals.pkl`.
- A configuration file in `04_repairing/config/`.

**File: `config/weighted_vc_repair.yaml`**
```yaml
_target_: src.repairing.weighted_vc_repairer.WeightedVCRepairer
alpha: 0.5
max_iterations: 10
```

## 2. What I expect to see (Process)
The repairer identifies where the synthetic data deviates from the marginals and performs iterative updates.

**Command:**
```powershell
# Move to the stage folder (Isolation)
cd icm_sandbox/04_repairing

# Execute using local input/ folder (Context Engineering)
python src/main.py --config config/weighted_vc_repair.yaml
```

## 3. What I will output (Output)
- `repaired_data.csv`: The updated synthetic dataset.
- `repair_log.json`: Iteration history and convergence info.
