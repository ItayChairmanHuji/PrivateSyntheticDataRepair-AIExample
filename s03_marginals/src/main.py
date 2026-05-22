import hydra
from omegaconf import DictConfig, OmegaConf
from s03_marginals.src.orchestration.stage_orchestrator import StageOrchestrator
from s03_marginals.src.loaders.artifact_loader import ArtifactLoader
from s03_marginals.src.io.artifact_saver import ArtifactSaver

@hydra.main(version_base=None, config_path="../config", config_name="top_k")
def main(cfg: DictConfig):
    # Filter out stage-level config from component instantiation
    dataset_name = cfg.dataset_name
    
    # Create a copy and remove dataset_name to avoid passing it to the component constructor
    component_cfg = OmegaConf.to_container(cfg, resolve=True)
    component_cfg.pop("dataset_name")

    obtainer = hydra.utils.instantiate(component_cfg)
    orchestrator = StageOrchestrator(
        loader=ArtifactLoader(),
        saver=ArtifactSaver(),
        obtainer=obtainer
    )
    orchestrator.run(dataset_name)

if __name__ == "__main__":
    main()
