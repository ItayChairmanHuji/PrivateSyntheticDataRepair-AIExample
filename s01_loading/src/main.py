import hydra
from omegaconf import DictConfig
from pathlib import Path
from s01_loading.src.orchestration import StageOrchestrator

@hydra.main(version_base=None, config_path="../config", config_name="adult100")
def main(cfg: DictConfig):
    dataset_name = cfg.get("dataset_name", cfg.name)
    output_dir = Path("s01_loading/output") / dataset_name
    
    # Create a clean copy for component instantiation (Membrane Pattern)
    from omegaconf import OmegaConf
    component_cfg = OmegaConf.to_container(cfg, resolve=True)
    component_cfg.pop("dataset_name", None)

    orchestrator = StageOrchestrator(
        loader=hydra.utils.instantiate(component_cfg),
        output_dir=output_dir
    )
    
    dataset = orchestrator.run()
    print(f"Success: Loaded {dataset_name} ({len(dataset)} rows).")

if __name__ == "__main__":
    main()
