import time
import hydra
from omegaconf import DictConfig
import pandas as pd
import os
import psutil

def print_memory():
    process = psutil.Process(os.getpid())
    print(f"Memory Usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")

@hydra.main(version_base=None, config_path="../config", config_name="config")
def benchmark(cfg: DictConfig):
    print(f"--- Benchmarking Census Dataset ---")
    print_memory()
    
    # 1. Loading
    print("\n--- Stage 1: Loading ---")
    start = time.time()
    loader = hydra.utils.instantiate(cfg.loading)
    private_dataset = loader.load()
    duration = time.time() - start
    print(f"Loading took: {duration:.2f}s")
    print_memory()
    
    # 2. Synthesizing
    print("\n--- Stage 2: Synthesizing (Model Loading) ---")
    start = time.time()
    synthesizer = hydra.utils.instantiate(cfg.synthesizing)
    synthetic_dataset = synthesizer.synthesize(private_dataset)
    duration = time.time() - start
    print(f"Synthesizing took: {duration:.2f}s")
    print_memory()
    
    # 3. Marginals Obtaining
    print("\n--- Stage 3: Marginals Obtaining ---")
    start = time.time()
    obtainer = hydra.utils.instantiate(cfg.marginals_obtaining)
    obtained_marginals = obtainer.obtain(private_dataset, synthetic_dataset)
    duration = time.time() - start
    print(f"Marginals Obtaining took: {duration:.2f}s")
    print_memory()
    
    # 4. Repairing
    print("\n--- Stage 4: Repairing (Skipped or Minimal) ---")
    # Repairing is usually the bottleneck for ILP, but let's see others first.
    # We might skip it or use a fast one for profiling other stages.
    
    # 5. Evaluating
    print("\n--- Stage 5: Evaluating ---")
    start = time.time()
    evaluator = hydra.utils.instantiate(cfg.evaluating)
    # Mocking a pipeline result to avoid full repair if needed, 
    # but here we want to see the evaluator's performance on full private data.
    from src.entities.pipeline_result import PipelineResult
    res = PipelineResult(
        private_dataset=private_dataset,
        synthetic_dataset=synthetic_dataset,
        repaired_dataset=synthetic_dataset, # Use synthetic as repaired for profiling evaluator
        obtained_marginals=obtained_marginals,
        runtimes={},
        metadata={}
    )
    evaluator.run(res)
    duration = time.time() - start
    print(f"Evaluating took: {duration:.2f}s")
    print_memory()

if __name__ == "__main__":
    benchmark()
