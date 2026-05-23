import hydra
from omegaconf import DictConfig, OmegaConf
from s03_marginals.src.orchestration.stage_orchestrator import StageOrchestrator
from s03_marginals.src.loaders.artifact_loader import ArtifactLoader
from s03_marginals.src.io.artifact_saver import ArtifactSaver
@hydra.main(version_base=None, config_path="../config", config_name="top_k")
def main(cfg: DictConfig):
    # Use .get() to avoid IDE warnings and handle missing keys safely
    experiment_name = cfg.get("experiment_name", cfg.get("dataset_name", "unknown"))

    # Create a clean copy for component instantiation (Membrane Pattern)
    component_cfg = OmegaConf.to_container(cfg, resolve=True)
    component_cfg.pop("dataset_name", None)
    component_cfg.pop("experiment_name", None)

    obtainer = hydra.utils.instantiate(component_cfg)
    orchestrator = StageOrchestrator(
        loader=ArtifactLoader(),
        saver=ArtifactSaver(),
        obtainer=obtainer
    )
    orchestrator.run(experiment_name)


if __name__ == "__main__":
    main()
