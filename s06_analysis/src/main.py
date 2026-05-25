import hydra
from omegaconf import DictConfig
from pathlib import Path
from s06_analysis.src.orchestration.stage_orchestrator import StageOrchestrator

@hydra.main(version_base=None, config_path="../config", config_name="experiment_4")
def main(cfg: DictConfig):
    # Setup paths
    experiment_name = cfg.get("experiment_name", "unknown_experiment")
    stage_root = Path(__file__).parent.parent
    output_dir = stage_root / cfg.get("output_dir", "notebooks")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Instantiate components via Hydra
    orchestrator = StageOrchestrator(
        loader=hydra.utils.instantiate(cfg.loader),
        generator=hydra.utils.instantiate(cfg.generator),
        flattener=hydra.utils.instantiate(cfg.flattener),
        output_dir=output_dir
    )

    # Run orchestration
    notebook_path = orchestrator.run(experiment_name=experiment_name)
    
    print(f"Success: Analysis notebook generated at {notebook_path}")

if __name__ == "__main__":
    main()
