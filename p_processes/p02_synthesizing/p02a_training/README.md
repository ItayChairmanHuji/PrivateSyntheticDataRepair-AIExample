# Process 02a: Training

## Purpose
Train a differentially private generative model on a private dataset.

## Parameter Identity
- **Inputs:** `r_resources/r_data/{dataset}/private/data.csv`
- **Outputs:** `r_resources/r_models/{dataset}/{synth}/{eps}/{seed}.pkl`

## Usage (CLI)
```bash
python -m p_processes.p02_synthesizing.p02a_training.main dataset_name=adult100 synthesizer_name=mst epsilon=0.1 seed=42
```

## Usage (Library)
```python
from p_processes.p02_synthesizing.p02a_training import train_model
model = train_model(dataset, cfg)
```
