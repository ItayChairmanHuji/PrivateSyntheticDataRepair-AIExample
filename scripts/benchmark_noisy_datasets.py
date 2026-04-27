
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

def run_benchmark(name):
    print(f"\n=== Benchmarking Noisy {name} ===")
    loader = get_loader(name)
    dataset = loader.load()
    print(f"Loaded {len(dataset.data)} rows.")
    
    # Using 50 iterations to match standard experiment configurations
    synthesizer = CoNoise(num_of_iterations=50, seed=42)
    print(f"Synthesizing noisy version...")
    start_syn = time.time()
    noisy_dataset = synthesizer.synthesize(dataset)
    print(f"Synthesis took: {time.time() - start_syn:.2f}s")
    
    print(f"Finding violations...")
    start = time.time()
    v = noisy_dataset.get_violations()
    duration = time.time() - start
    print(f"Violation Detection Time: {duration:.4f}s")
    print(f"Total Violations Found: {len(v)}")
    return duration, len(v)

if __name__ == "__main__":
    datasets = ["adult", "compas", "tax", "census"]
    summary = []
    for ds in datasets:
        try:
            t, count = run_benchmark(ds)
            summary.append({"Dataset": ds, "Time (s)": f"{t:.2f}", "Violations": count})
        except Exception as e:
            print(f"Error benchmarking {ds}: {e}")
            
    print("\n\n=== Final Summary ===")
    print(pd.DataFrame(summary).to_string(index=False))
