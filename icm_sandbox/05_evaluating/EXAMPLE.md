# Stage 05 Execution Example: Final Evaluation

## 1. What you need to insert (Input)
- `private_data.csv`, `synthetic_data.csv`, and `repaired_data.csv`.

**File: `config/default_eval.yaml`**
```yaml
metrics:
  - total_variation_distance
  - violation_count
  - range_query_error
```

## 2. What I expect to see (Process)
The evaluator runs a battery of tests comparing the three datasets.

**Command:**
```powershell
python 05_evaluating/src/main.py --config default_eval.yaml --in_all stages_outputs/
```

## 3. What I will output (Output)
- `results.json`: All metrics in a single flat JSON file.
