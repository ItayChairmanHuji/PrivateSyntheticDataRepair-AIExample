# Utils Context

## Goal
The `utils` package provides shared helper functions and utilities that are used across various components of the research framework.

## Key Utilities

### 1. Serialization Helper (`serialization_helper.py`)
- **Purpose**: Prepares complex objects (like datasets or experiment results) for JSON serialization.
- **Logic**: Recursively extracts public attributes, handles NumPy arrays (converting to lists), and processes nested objects.

### 2. Gurobi Helper (`gurobi_helper.py`)
- **Purpose**: Manages Gurobi environment initialization and licensing.
- **Logic**: Ensures a single centralized point for Gurobi configuration to avoid license initialization overhead.

## Testing
Utilities are verified in `tests/utils/`.

### 1. Serialization Helper Tests (`test_serialization_helper.py`)
- **NumPy Serialization**: Verifies that NumPy arrays are correctly converted to serializable Python lists.
- **Object Extraction**: Ensures that `get_serializable_params` correctly extracts public attributes while ignoring private members (starting with `_`).
- **Nesting**: Validates that nested objects and dictionaries are processed recursively.
- **Type Handling**: Checks robustness against various types including `None`, `int`, `float`, and `str`.
