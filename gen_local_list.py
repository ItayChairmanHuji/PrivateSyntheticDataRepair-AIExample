import os
local = [d for d in os.listdir('results') if d.startswith('alpha_sweep_may2026')]
with open('local_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(local))
print(f"Wrote {len(local)} names to local_results.txt")
