import os
import subprocess

if not os.path.exists('local_results.txt'):
    print("local_results.txt not found. Please upload it first.")
    exit(1)

with open('local_results.txt', 'r', encoding='utf-8') as f:
    local = set(line.strip() for line in f if line.strip())

remote_results_dir = 'results'
all_remote = [d for d in os.listdir(remote_results_dir) if os.path.isdir(os.path.join(remote_results_dir, d))]
missing = [os.path.join(remote_results_dir, d) for d in all_remote if d not in local]

print(f"Total remote: {len(all_remote)}")
print(f"Total local: {len(local)}")
print(f"Missing (new): {len(missing)}")

if missing:
    zip_file = 'new_results.zip'
    if os.path.exists(zip_file):
        os.remove(zip_file)
        
    # Zip in chunks to avoid argument length limits
    chunk_size = 50
    for i in range(0, len(missing), chunk_size):
        chunk = missing[i:i+chunk_size]
        print(f"Zipping chunk {i//chunk_size + 1}/{(len(missing)-1)//chunk_size + 1}...")
        cmd = ['zip', '-r', zip_file] + chunk
        subprocess.run(cmd, capture_output=True)
    print(f"Zipping complete: {zip_file}")
else:
    print("No missing results found.")
