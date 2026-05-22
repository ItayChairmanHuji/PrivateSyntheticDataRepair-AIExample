import hydra
from omegaconf import DictConfig
from s04_repairing.src.orchestration import StageOrchestrator
from s04_repairing.src.io import FileLoader, ArtifactSaver

@hydra.main(version_base=None, config_path="../config", config_name="vanilla_vc")
def main(cfg: DictConfig):
    dataset_name = cfg.get("dataset_name")
    if not dataset_name:
        print("Error: dataset_name must be provided in config or as an argument (e.g., dataset_name=adult100)")
        return

    # 1. Instantiate Domain Component (Repairer)
    repairer = hydra.utils.instantiate(cfg)

    # 2. Instantiate IO Components
    loader = FileLoader(dataset_name=dataset_name)
    saver = ArtifactSaver(dataset_name=dataset_name)

    # 3. Orchestrate
    orchestrator = StageOrchestrator(
        dataset_name=dataset_name,
        repairer=repairer,
        loader=loader,
        saver=saver
    )
    orchestrator.run()

if __name__ == "__main__":
    main()
