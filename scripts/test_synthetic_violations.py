
import pandas as pd
import time
import multiprocessing
from src.loading.file_loader import FileLoader
from src.loading.components.data_loader import DataLoader
from src.loading.components.dcs_loader import DCsLoader
from src.loading.components.metadata_loader import MetadataLoader
from src.loading.components.data_encoder import DataEncoder
from src.loading.components.dcs_encoder import DCsEncoder
from src.synthesizing.co_noise import CoNoise

def run_test(ds_name, result_dict):
    try:
        loader = FileLoader(
            name=ds_name, 
            base_path="data",
            data_loader=DataLoader(),
            dcs_loader=DCsLoader(),
            metadata_loader=MetadataLoader(),
            data_encoder=DataEncoder(),
            dcs_encoder=DCsEncoder()
        )
        dataset = loader.load()
        print(f"Loaded {ds_name}. Adding violations with Co-Noise...")
        
        synthesizer = CoNoise(num_of_iterations=100)
        synthetic_dataset = synthesizer.synthesize(dataset)
        
        print(f"Starting violation finding for {ds_name}_synthetic...")
        start_time = time.time()
        violations = synthetic_dataset.get_violations()
        end_time = time.time()
        
        result_dict['status'] = 'success'
        result_dict['count'] = len(violations)
        result_dict['time'] = end_time - start_time
    except Exception as e:
        result_dict['status'] = 'error'
        result_dict['message'] = str(e)

def test_dataset(ds_name, timeout_seconds=180):
    print(f"\n--- Testing Synthetic {ds_name} (Timeout: {timeout_seconds}s) ---")
    
    manager = multiprocessing.Manager()
    result_dict = manager.dict()
    
    p = multiprocessing.Process(target=run_test, args=(ds_name, result_dict))
    p.start()
    p.join(timeout_seconds)
    
    if p.is_alive():
        p.terminate()
        p.join()
        print(f"FAILED: Violation finding for {ds_name}_synthetic timed out after {timeout_seconds}s!")
    else:
        if result_dict.get('status') == 'success':
            print(f"Success! Found {result_dict['count']} violations in {result_dict['time']:.2f}s.")
        else:
            print(f"Error processing {ds_name}: {result_dict.get('message')}")

if __name__ == "__main__":
    test_dataset("tax", timeout_seconds=120)
    test_dataset("census", timeout_seconds=120)
