
import os
from collections import Counter

log_dir = "logs/may_2026_batch"
files = os.listdir(log_dir)
out_files = [f for f in files if f.endswith(".out")]

indices = []
for f in out_files:
    parts = f.split("_")
    # may_2026_batch_INDEX_JOBID.out
    if len(parts) >= 4:
        try:
            indices.append(int(parts[3]))
        except ValueError:
            pass

counter = Counter(indices)
duplicates = {k: v for k, v in counter.items() if v > 1}

print(f"Total .out files: {len(out_files)}")
print(f"Unique indices: {len(counter)}")
print(f"Duplicates: {duplicates}")

# Check which ones are small
small_indices = []
for f in out_files:
    if os.path.getsize(os.path.join(log_dir, f)) < 200:
        parts = f.split("_")
        if len(parts) >= 4:
            small_indices.append(parts[3])

print(f"Small log files (indices): {small_indices}")
