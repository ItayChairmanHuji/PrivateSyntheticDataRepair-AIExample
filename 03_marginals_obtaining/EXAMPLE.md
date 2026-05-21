# Stage 03 Execution Example: Obtaining Top-K Marginals

This example shows how to calculate noisy marginals from the private data.

## 1. What you need to insert (Input)
- `private_data.csv` and `synthetic_data.csv`.
- A configuration file in `03_marginals_obtaining/config/`.

**File: `config/top_k_marginals.yaml`**
```yaml
_target_: src.marginals_obtaining.top_k.TopKMarginals
k: 50
epsilon: 0.1 # DP budget for the marginals themselves
```

## 2. What I expect to see (Process)
The script calculates which marginals have the highest error or are most important, then computes them with DP noise.

**Command:**
```powershell
python 03_marginals_obtaining/src/main.py --config top_k_marginals.yaml --in_private 01_loading/output --in_synthetic 02_synthesizing/output
```

## 3. What I will output (Output)
- `marginals.pkl`: A serialized `MarginalSet` object.
- `marginal_stats.json`: Coverage and error statistics.
