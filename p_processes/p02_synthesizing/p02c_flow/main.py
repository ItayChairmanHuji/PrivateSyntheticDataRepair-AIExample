import hydra
from omegaconf import DictConfig, OmegaConf
from p_processes.p02_synthesizing.p02a_training.src.orchestration.training_orchestrator import TrainingWorker
from p_processes.p02_synthesizing.p02b_sampling.src.orchestration.sampling_orchestrator import SamplingWorker
from p_processes.p02_synthesizing.p02b_sampling.src.bridge.sampling_bridge import SamplingBridge
from p_processes.p02_synthesizing.p02b_sampling.src.core.sampling_core import SamplingCore
from u_utilities.u_io import ResourceManager

@hydra.main(version_base=None, config_path="../config", config_name="mst")
def main(cfg: DictConfig):
    print("Starting Orchestrated Synthesis Flow (p02c)...")
    
    # 1. Training
    print("--- Stage 1: Training ---")
    
    if "training" in cfg:
        target_cfg = cfg.training
    elif "synthesizing" in cfg:
        target_cfg = cfg.synthesizing
    else:
        target_cfg = cfg

    trainer = hydra.utils.instantiate(target_cfg)
    train_worker = TrainingWorker()
    model_path = train_worker.run(target_cfg, trainer)
    
    # 2. Sampling (passing the model directly to avoid serialization issues in same process)
    print("--- Stage 2: Sampling ---")
    manager = ResourceManager()
    
    bridge = SamplingBridge(manager=manager)
    core = SamplingCore(sampler=trainer) # trainer is also the sampler for SmartNoise
    
    sample_worker = SamplingWorker(
        bridge=bridge,
        core=core,
        dataset_name=target_cfg.dataset_name,
        engine_name=target_cfg.engine,
        epsilon=target_cfg.epsilon,
        seed=target_cfg.seed,
        size=target_cfg.get("size", 100)
    )
    
    # Manually execute sampling if load_model failed (it likely will fail due to the bug)
    try:
        sample_worker.run()
    except Exception as e:
        print(f"Warning: Sampling failed during load_model: {e}")
        print("Attempting to sample directly from the trained object...")
        # Direct sampling bypasses the file I/O for the model
        dataset = manager.load_dataset(target_cfg.dataset_name)
        gen_size = target_cfg.get("size", 100)
        synthetic_dataset = core.sample(trainer, dataset, gen_size)
        
        output_path = bridge.resolve_synthetic_data_path(
            target_cfg.dataset_name, target_cfg.engine, target_cfg.epsilon, target_cfg.seed, gen_size
        )
        manager.save_dataset(synthetic_dataset, output_path.parent)
        print(f"Success [Direct Sampling]: {target_cfg.dataset_name} -> {output_path}")

    print("Success [p02c_flow]: Orchestration complete.")

if __name__ == "__main__":
    main()
