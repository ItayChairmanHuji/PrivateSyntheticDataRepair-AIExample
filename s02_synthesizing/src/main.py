import hydra
from omegaconf import DictConfig
from pathlib import Path
import sys

# Ensure project root is in path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from shared.utils.mbi_patch import apply_patch
from s02_synthesizing.src.orchestration.stage_orchestrator import StageOrchestrator

# Apply reproducibility patch for mbi
apply_patch()

@hydra.main(version_base=None, config_path="../config", config_name="mst")
def main(cfg: DictConfig):
    dataset_name = cfg.get("dataset_name", "adult100")
    mode = cfg.get("mode", "full")
    output_dir = Path("s02_synthesizing/output") / dataset_name
    
    print(f"--- Stage 2: Synthesizing Dataset '{dataset_name}' (Mode: {mode}) ---")
    
    # 1. Instantiate the orchestrator
    orchestrator = StageOrchestrator(
        synthesizer=hydra.utils.instantiate(cfg),
        output_dir=output_dir,
        mode=mode
    )
    
    # 2. Run the stage
    orchestrator.run()
    
    print(f"Success: Stage 2 completed for {dataset_name}.")

if __name__ == "__main__":
    main()
