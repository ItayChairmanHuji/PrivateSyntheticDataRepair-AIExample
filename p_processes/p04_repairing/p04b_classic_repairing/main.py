import hydra
from omegaconf import DictConfig
from p_processes.p04_repairing.src.worker import RepairingWorker

@hydra.main(version_base=None, config_path="../config", config_name="classic")
def main(cfg: DictConfig):
    worker: RepairingWorker = hydra.utils.instantiate(cfg)
    worker.run()

if __name__ == "__main__":
    main()
