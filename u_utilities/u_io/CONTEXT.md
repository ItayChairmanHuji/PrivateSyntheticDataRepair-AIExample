# Utility: u_io (Resource Manager)

## Purpose
The "Linker" of the RPM architecture. It translates abstract parameters into physical file paths in `r_resources/` and handles all I/O operations through specialized loaders and a centralized path resolver.

## Technical Documentation (The "Glass Box")
For a deep dive into the implementation, architectural logic, and "Smart Discovery" algorithms, see:
👉 **[`src/internal_readme.md`](src/internal_readme.md)**

## Interface
- **`ResourceManager`**: The primary facade for the utility. It orchestrates path resolution via `PathResolver` and delegates I/O to specialized loaders.
- **`PathResolver`**: The unified path finding engine. It uses a central `resolve` method to generate deterministic paths for all resource types.
- **`DataMode` (Enum)**: Defines the dataset stage (`PRIVATE`, `SYNTHETIC`, `REPAIRED`).
- **`Loaders`**: Specialized classes for different data types (e.g., `DataLoader`, `ModelLoader`).

## Usage

### High-Level (Resource Manager)
```python
from u_utilities.u_io import ResourceManager, DataMode

manager = ResourceManager()

# Load a base dataset (Defaults to PRIVATE)
dataset = manager.load_dataset("adult100")

# Load synthetic data (Smartly handles context/metadata discovery)
synth_dataset = manager.load_dataset(
    name="adult100",
    mode=DataMode.SYNTHETIC,
    synth_name="aim",
    epsilon=1.0,
    seed=42,
    size=1000
)
```

### Low-Level (Path Resolver)
```python
from u_utilities.u_io import PathResolver

resolver = PathResolver()
path = resolver.resolve("model", dataset_name="adult100", synth_name="aim", epsilon=1.0, seed=42)
```
