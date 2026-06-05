import hydra
from omegaconf import DictConfig
from p_processes.p02a_training.main import main as train_main
from p_processes.p02b_sampling.main import main as sample_main

@hydra.main(version_base=None, config_path="../../r_resources/r_configs/base", config_name="synthesizing/mst")
def main(cfg: DictConfig):
    print("Starting Orchestrated Synthesis (p02c)...")
    
    # Run Training
    train_main(cfg)
    
    # Run Sampling
    sample_main(cfg)
    
    print("Success [p02c_synthesizing]: Orchestration complete.")

if __name__ == "__main__":
    main()
