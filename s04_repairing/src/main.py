import hydra
from omegaconf import DictConfig
from s04_repairing.src.orchestration import StageOrchestrator
from s04_repairing.src.io import FileLoader, ArtifactSaver

@hydra.main(version_base=None, config_path="../config", config_name="vanilla_vc")
def main(cfg: DictConfig):
    experiment_name = cfg.get("experiment_name", cfg.get("dataset_name"))
    if not experiment_name:
        print("Error: experiment_name or dataset_name must be provided (e.g., ++dataset_name=adult100)")
        return

    # Create a clean copy for component instantiation (Membrane Pattern)
    from omegaconf import OmegaConf
    component_cfg = OmegaConf.to_container(cfg, resolve=True)
    component_cfg.pop("dataset_name", None)
    component_cfg.pop("experiment_name", None)

    # 1. Instantiate Domain Component (Repairer)
    repairer = hydra.utils.instantiate(component_cfg)

    # 2. Instantiate IO Components
    loader = FileLoader(experiment_name=experiment_name)
    saver = ArtifactSaver(experiment_name=experiment_name)

    # 3. Orchestrate
    orchestrator = StageOrchestrator(
        experiment_name=experiment_name,
        repairer=repairer,
        loader=loader,
        saver=saver
    )
    orchestrator.run()

if __name__ == "__main__":
    main()
