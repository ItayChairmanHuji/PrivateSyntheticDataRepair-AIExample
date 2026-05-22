# Marginals Context

## Goal
The marginals stage is responsible for selecting and generating noisy k-way marginals from the private and synthetic datasets to be used in the repair process.

## Key Components

### 1. Orchestration (`orchestration/`)
- **StageOrchestrator**: The central brain. It wires together the `ArtifactLoader` from `loaders/`, the `ArtifactSaver` from `io/`, and the `Obtainer` from `marginals/`.

### 2. Infrastructure & I/O (`io/`)
- **ArtifactSaver**: Handles standardized export of marginals as JSON.
- **CLI Tools**: `clean.py`.

### 3. Loaders (`loaders/`)
- **ArtifactLoader**: Loads private data, synthetic data, metadata, and constraints.

### 4. Domain Specific: Marginals (`marginals/`)
- **TopKObtainer**: Implements the Top-K selection and noisy generation of marginals.
- **UtilityFunction**: Abstract base for marginal scoring.
- **DistanceUtility**: Utility based on absolute frequency difference.
