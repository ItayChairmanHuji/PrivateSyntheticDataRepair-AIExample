from pathlib import Path

def list_datasets():
    config_dir = Path("s01_loading/config")
    if not config_dir.exists():
        print(f"Config directory {config_dir} not found.")
        return
    
    # Filter for yaml files, excluding some generic ones if they exist
    configs = [f.stem for f in config_dir.glob("*.yaml") if f.stem not in ["file_loader"]]
    
    print("Available dataset configurations:")
    for cfg in sorted(configs):
        print(f"  - {cfg}")

if __name__ == "__main__":
    list_datasets()
