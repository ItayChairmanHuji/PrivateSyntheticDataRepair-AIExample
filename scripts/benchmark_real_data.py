
import time
import pandas as pd
from src.loading.file_loader import FileLoader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder
from src.synthesizing.co_noise import CoNoise

def get_loader(name):
    return FileLoader(
        name=name,
        base_path="data",
        data_loader=DataLoader(),
        dcs_loader=DCsLoader(),
        metadata_loader=MetadataLoader(),
        data_encoder=DataEncoder(),
        dcs_encoder=DCsEncoder()
    )

def run_real_benchmark(name):
    print(f"\n=== Benchmarking {name} ===")
    loader = get_loader(name)
    dataset = loader.load()
    print(f"Loaded {len(dataset.data)} rows.")
    
    # 1. Test real data (expect 0 violations)
    start = time.time()
    v = dataset.get_violations()
    end = time.time()
    print(f"Time to check real data (0 violations): {end - start:.4f}s")
    
    # 2. Test synthesized data (noisy)
    # We use fewer iterations for CoNoise just to seed some violations
    print(f"Synthesizing noisy version of {name}...")
    synthesizer = CoNoise(num_of_iterations=100, seed=42)
    noisy_dataset = synthesizer.synthesize(dataset)
    
    print(f"Checking violations in noisy {name}...")
    start = time.time()
    # No limits!
    v_noisy = noisy_dataset.get_violations()
    end = time.time()
    print(f"Time to find ALL violations in noisy data: {end - start:.4f}s")
    print(f"Found {len(v_noisy)} violations.")

if __name__ == "__main__":
    run_real_benchmark("tax")
    run_real_benchmark("census")
