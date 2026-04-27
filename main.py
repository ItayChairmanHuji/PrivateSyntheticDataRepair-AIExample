import hydra
from omegaconf import DictConfig
from src.pipeline import Pipeline

@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    # Instantiate the pipeline using Hydra's instantiation
    # This automatically builds the nested objects defined in YAML
    pipeline: Pipeline = hydra.utils.instantiate(cfg.pipeline)
    pipeline.run()

if __name__ == "__main__":
    main()
