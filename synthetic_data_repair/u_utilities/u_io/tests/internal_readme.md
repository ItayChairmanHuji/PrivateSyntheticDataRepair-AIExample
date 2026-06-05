# u_io Test Suite Documentation

This directory contains the automated test suite for the `u_io` utility. The tests are designed to verify the core contracts of path resolution, resource loading, and the autonomous context discovery mechanism.

## Test Philosophy
We use a **Mock-Hierarchy** approach. Instead of relying on the actual `r_resources` folder, each test creates a temporary, localized RPM-native folder structure. This ensures that the tests are hermetic and verify the *logic* of the utility rather than the state of the actual project.

## Test Cases (`test_io.py`)

### `test_path_resolver`
Verifies that the `PathResolver` correctly translates parameters into the expected RPM directory hierarchy.
- **Coverage**: 
    - Private data directory resolution.
    - Synthetic data file path construction (deep hierarchy).

### `test_data_loader_discovery`
Verifies the **Autonomous Context Discovery** (`_discover_context`) mechanism in `DataLoader`.
- **Scenario**: 
    1. Create a mock structure: `r_data/adult/private` and `r_data/adult/synthetic/...`.
    2. Attempt to load the synthetic CSV.
- **Assertion**: The loader must successfully find and load the metadata and constraints from the sibling `private/` folder by walking up the tree.

### `test_resource_manager_di`
Verifies the **Dependency Injection** and **Facade Integration**.
- **Scenario**: Initialize a `ResourceManager` with a resolver pointing to a custom temporary root.
- **Assertion**: Both private and synthetic datasets must be correctly loaded through the manager, proving that the dispatcher and loaders are wired correctly.

## Running Tests
Ensure the project root is in your `PYTHONPATH`:
```bash
$env:PYTHONPATH = "synthetic_data_repair;."
pytest synthetic_data_repair/u_utilities/u_io/tests/test_io.py
```
