import os
local = [d for d in os.listdir('results') if os.path.isdir(os.path.join('results', d))]
with open('local_results.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(local))
print(f"Wrote {len(local)} names to local_results.txt")
