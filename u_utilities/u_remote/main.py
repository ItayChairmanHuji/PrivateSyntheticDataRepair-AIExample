import hydra
from omegaconf import DictConfig
from u_utilities.u_remote.src.facade import RemoteFacade

@hydra.main(version_base=None, config_path="config", config_name="default")
def main(cfg: DictConfig):
    facade = RemoteFacade(cfg.remote_host, cfg.remote_dir)
    
    if cfg.mode == "push":
        facade.push_codebase()
    elif cfg.mode == "push_resources":
        facade.push_resources()
    elif cfg.mode == "setup":
        facade.setup_environment()
    elif cfg.mode == "pull":
        facade.pull_results(cfg.experiment_id)
    else:
        print(f"Unknown mode: {cfg.mode}")

if __name__ == "__main__":
    main()
