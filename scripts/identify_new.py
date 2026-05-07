import os
import json
from pathlib import Path

def find_new_experiments(results_dir):
    new_exps = []
    for root, _, files in os.walk(results_dir):
        for f in files:
            if f.endswith('.json') and f.startswith('result_'):
                path = Path(root) / f
                try:
                    with open(path, 'r') as jf:
                        data = json.load(jf)
                        timestamp = data.get('timestamp', '')
                        metadata = data.get('metadata', {})
                        synth = metadata.get('synthesizer', '')
                        
                        if '2026-05-06' in timestamp:
                            # Also check for aim, mst, patectgan
                            synth_params = metadata.get('synthesizer_params', {})
                            engine = synth_params.get('engine', '')
                            model_path = synth_params.get('model_path', '')
                            
                            is_target = any(e in engine.lower() or e in str(model_path).lower() 
                                           for e in ['aim', 'mst', 'patectgan'])
                            
                            new_exps.append({
                                'path': str(path),
                                'synth': synth,
                                'engine': engine,
                                'model_path': model_path,
                                'timestamp': timestamp,
                                'is_target': is_target
                            })
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    return new_exps

results = find_new_experiments('results')
print(f"Found {len(results)} experiments from 2026-05-06 in 'results/'")
target_results = [r for root, r in enumerate(results) if results[root]['is_target']]
print(f"Found {len(target_results)} target experiments (aim/mst/patectgan) from 2026-05-06 in 'results/'")

for r in target_results[:10]:
    print(f"{r['path']} - {r['synth']} - {r['timestamp']}")

results_old = find_new_experiments('results_old')
print(f"\nFound {len(results_old)} experiments from 2026-05-06 in 'results_old/'")
target_results_old = [r for root, r in enumerate(results_old) if results_old[root]['is_target']]
print(f"Found {len(target_results_old)} target experiments (aim/mst/patectgan) from 2026-05-06 in 'results_old/'")

for r in target_results_old[:10]:
    print(f"{r['path']} - {r['synth']} - {r['timestamp']}")
