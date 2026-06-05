# Process: p02a_training

## Purpose
Trains a generative model (Synthesizer) on a private dataset and saves the model artifact.

## Contract
- **Input Resource**: `r_resources/r_data/private/{dataset_name}/data.csv`
- **Output Resource**: `r_resources/r_models/{dataset_name}/{synth}/{eps}/{seed}/model.pkl`

## Usage
```bash
python -m p_processes.p02a_training.main dataset_name=adult100 epsilon=1.0
```
