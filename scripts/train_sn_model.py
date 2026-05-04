import os
import dill
import hydra
from omegaconf import DictConfig, OmegaConf
from snsynth import Synthesizer as SnSynthesizer
import pandas as pd
from pathlib import Path

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

@hydra.main(version_base=None, config_path="../config", config_name="config")
def train(cfg: DictConfig):
    # Ensure we use adult100 if requested or by default for this task
    # We can override via CLI: loading.name=adult100
    
    loader = hydra.utils.instantiate(cfg.loading)
    dataset = loader.load()
    
    # We expect synthesizing to be one of the smartnoise models
    # e.g. synthesizing=mst
    engine = cfg.synthesizing.engine
    epsilon = cfg.synthesizing.epsilon
    
    # Extract kwargs if they exist
    kwargs = {}
    if "kwargs" in cfg.synthesizing:
        kwargs = OmegaConf.to_container(cfg.synthesizing.kwargs, resolve=True)
    
    print(f"Training {engine} on {dataset.name} with epsilon={epsilon}...")
    synth = SnSynthesizer.create(engine, epsilon=epsilon, **kwargs)
    synth.fit(dataset.data, categorical_columns=dataset.data.columns.tolist())
    
    # Save model
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    model_path = models_dir / f"{dataset.name}_{engine}.pkl"
    
    with open(model_path, "wb") as f:
        dill.dump(synth, f)
    
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
