import os
import subprocess
from pathlib import Path

def is_complete(path):
    if not os.path.exists(path): return False
    return any(f.endswith('.json') for f in os.listdir(path))

local_dirs = ['results', 'results_alpha_eps01/results', 'results_may15/results', 'results_may2026_weighted/results']
complete_local = set()

for d in local_dirs:
    if os.path.exists(d):
        for entry in os.listdir(d):
            if is_complete(os.path.join(d, entry)):
                complete_local.add(entry)

with open('complete_local.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(complete_local))

print(f"Total complete local results: {len(complete_local)}")
