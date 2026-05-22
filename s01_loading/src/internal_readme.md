# Loading Context

## Goal
The loading stage is responsible for reading private datasets, metadata, and denial constraints, and identifying all initial violations in the data.

## Key Components

### 1. Orchestration (`orchestration/`)
- **StageOrchestrator**: The central brain. It wires together the `FileLoader` from `io/` and the encoders from `encoders/`.

### 2. Infrastructure & I/O (`io/`)
- **FileLoader**: Orchestrates the multi-step loading process (Load -> Sample -> Encode).
- **ArtifactSaver**: Handles standardized export of results.
- **CLI Tools**: `clean.py` and `list_datasets.py`.

### 3. Loaders (`loaders/`)
- **DataLoader**: Reads raw CSV data.
- **DCsLoader**: Parses Denial Constraints from text.
- **MetadataLoader**: Loads JSON metadata.

### 4. Domain Specific: Encoders (`encoders/`)
- **DataEncoder**: Numeric transformation of categorical attributes.
- **DCsEncoder**: Re-mapping Denial Constraints to the numeric space.
