# Process: p02b_sampling

## Purpose
Generates synthetic data from a pre-trained model stored in `r_resources/r_models/`.

## Contract
- **Input Resource**: `r_resources/r_models/{dataset_name}/{synth}/{eps}/{seed}/model.pkl`
- **Output Resource**: `r_resources/r_data/synthetic/{dataset_name}/{synth}/{eps}/{seed}/{size}/data.csv`

## Usage
```bash
python -m p_processes.p02_synthesizing.p02b_sampling.main dataset_name=adult100 epsilon=1.0 size=10000
```
