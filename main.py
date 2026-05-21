import hydra
from omegaconf import DictConfig
from src.pipeline import Pipeline
from src.utils.mbi_patch import apply_patch

# Apply reproducibility patch for AIM/mbi
apply_patch()

@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    print(f"--- Starting Pipeline: {cfg.experiment_name} ---", flush=True)
    # Instantiate the pipeline using Hydra's instantiation
    # This automatically builds the nested objects defined in YAML
    pipeline: Pipeline = hydra.utils.instantiate(cfg.pipeline)
    pipeline.run()

if __name__ == "__main__":
    main()
