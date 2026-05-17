import os
import subprocess

with open('local_results.txt', 'r') as f:
    local = set(line.strip() for line in f if line.strip())

remote_results_dir = 'results'
all_remote = [d for d in os.listdir(remote_results_dir) if d.startswith('alpha_sweep_may2026')]
missing = [os.path.join(remote_results_dir, d) for d in all_remote if d not in local]

print(f"Total remote: {len(all_remote)}")
print(f"Total local: {len(local)}")
print(f"Missing: {len(missing)}")

if missing:
    # Zip in chunks to avoid argument length limits if many files
    chunk_size = 100
    for i in range(0, len(missing), chunk_size):
        chunk = missing[i:i+chunk_size]
        cmd = ['zip', '-r', 'missing_results.zip'] + chunk
        subprocess.run(cmd)
    print("Zipping complete: missing_results.zip")
else:
    print("No missing results found.")
