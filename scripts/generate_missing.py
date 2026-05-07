
def generate_missing():
    # Load all overrides
    with open("full_grid_overrides.txt", "r") as f:
        all_overrides = [line.strip() for line in f if line.strip()]
    
    # Indices to re-run
    to_rerun = list(range(80, 88)) + list(range(128, 180))
    
    missing = [all_overrides[i] for i in to_rerun]
    return missing

if __name__ == "__main__":
    missing = generate_missing()
    with open("missing_overrides.txt", "w") as f:
        for o in missing:
            f.write(o + "\n")
    print(f"Generated {len(missing)} missing experiments.")
