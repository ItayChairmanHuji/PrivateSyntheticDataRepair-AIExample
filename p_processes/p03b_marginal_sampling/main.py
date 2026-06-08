import hydra
from omegaconf import DictConfig

@hydra.main(version_base=None, config_path="config", config_name="default")
def main(cfg: DictConfig):
    worker = hydra.utils.instantiate(cfg)
    worker.run()

if __name__ == "__main__":
    main()
