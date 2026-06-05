# u_io Internal Documentation: The Glass Box Blueprint

This directory contains the core logic for the RPM Resource Management system. This document serves as the implementation blueprint, explaining exactly how the system functions so it can be understood, verified, or rebuilt from scratch without reading the source code.

## 1. Architectural Logic: The Three-Tier Flow

The utility operates on a strict **Resolve -> Load** sequence:
1.  **Request**: User provides high-level parameters.
2.  **Resolution**: `PathResolver` translates these into a physical path.
3.  **Loading**: The `ResourceManager` passes this path to a specialized `Loader`.
4.  **Context Stitching**: If the loader (e.g., `DataLoader`) detects that the target is a generated artifact, it autonomously finds the original metadata.

---

## 2. Component Blueprints

### `ResourceManager` (The Orchestrator)
- **Role**: The high-level facade and Dependency Injection container.
- **Hybrid API Pattern**: All methods support `(path: Optional[Path] = None, **kwargs)`. If `path` is missing, it calls `resolver.resolve(category, **kwargs)`.
- **Delegation**: Methods map directly to loader attributes:
    - `data`: `DataLoader`
    - `models`: `ModelLoader`
    - `marginals`: `MarginalLoader`
    - `results`: `ResultLoader`

### `PathResolver` (The Hierarchy Engine)
- **State**: Centralizes all root folder paths (`r_data`, `r_models`, `r_marginals`, `r_results`).
- **Resolution Categories**:
    - `data`: Handles PRIVATE (dataset/private), SYNTHETIC (deep parameters), and REPAIRED (deep parameters + alpha).
    - `model`: Maps `{dataset}/{synth}/{eps}/{seed}.pkl`.
    - `marginal`: Maps `{dataset}/{noise_level}/marginals.json`.
    - `result`: Maps `{experiment_id}/{timestamp}/`.

### `DataLoader` (The Smart Loader)
- **Autonomous Discovery**: Walks up from a data file to find the dataset root (where `parent.parent == "r_data"`). Returns `{root}/private`.
- **Load Logic**: Loads the CSV via Pandas, then loads `metadata.json` and `dcs.txt` from the discovered private context directory to return a complete `Dataset` object.

### `DCsLoader` (The Regex Parser)
- **Format**: `not(predicate & predicate)`.
- **Predicates**: `t(idx).(attr) (opr) (value)`.
- **Operators**: `=|!=|<=|>=|<|>`.
- **Logic**: Splits by `&`, parses components using regex, and instantiates the `DenialConstraints` object hierarchy. Returns empty constraints if the file is missing.

### `MetadataLoader` & `ResultLoader` (JSON Handlers)
- **Logic**: Standard JSON `load`/`dump`. 
- **Resilience**: `MetadataLoader` returns an empty dict `{}` if the file is missing to prevent pipeline crashes.

### `MarginalLoader` (Domain Handler)
- **Logic**: JSON serialization.
- **Contract**: Delegates actual dictionary transformation to the `MarginalSet.from_dict()` and `to_dict()` methods from `u_shared`.

### `ModelLoader` (Binary Handler)
- **Logic**: Binary I/O using Python's `pickle` module. Used for trained synthesizers and models.

---

## 3. Data Hierarchy Specification (RPM v1)

- **Private**: `r_resources/r_data/{name}/private/` (`data.csv`, `metadata.json`, `dcs.txt`)
- **Synthetic**: `r_resources/r_data/{name}/synthetic/{synth}/{eps}/{seed}/{size}/data.csv`
- **Repaired**: `r_resources/r_data/{name}/repaired/{repairer}/{synth}/{eps}/{seed}/{size}/{alpha}/data.csv`
- **Models**: `r_resources/r_models/{name}/{synth}/{eps}/{seed}.pkl`
- **Marginals**: `r_resources/r_marginals/{name}/{noise_level}/marginals.json`
- **Results**: `r_resources/r_results/{experiment_id}/{timestamp}/`

---

## 4. Design Principles
- **Separation of Concerns**: `PathResolver` (Where), `Loaders` (How), `ResourceManager` (When).
- **Parameter Identity**: The folder structure is the source of truth for resource identity.
- **Glass Box**: No hidden state; all resolution is deterministic and inspectable via the filesystem.
