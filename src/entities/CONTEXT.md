# Entities Context

## Goal
The `entities` package defines the core data structures used throughout the research framework. These entities ensure type safety and provide a common language for the different pipeline stages.

## Key Entities

### 1. Dataset & DatasetWithViolations (`dataset.py`)
- **Dataset**: A base container for data (Pandas DataFrame), denial constraints, and metadata.
- **DatasetWithViolations**: Extends `Dataset` with logic to find and cache violations using the `ViolationFinder`.

### 2. Denial Constraints (`denial_constraints.py`)
- **Side**: Represents one side of a predicate (attribute or literal value).
- **Predicate**: A comparison between two `Side` objects (e.g., `t1.Age > 20`).
- **DenialConstraint**: A collection of predicates that together define a forbidden state.
- **DenialConstraints**: A container for multiple `DenialConstraint` objects.

### 3. Marginals (`marginal.py`)
- **Marginal**: Represents a statistical property (e.g., a 2-way joint distribution frequency).
- **MarginalSet**: A collection of `Marginal` objects.

### 4. Pipeline Result (`pipeline_result.py`)
- **PipelineResult**: Holds the complete output of a pipeline run, including all dataset versions, obtained marginals, and runtimes.

## Testing
Core entity logic is verified in `tests/entities/`.

### 1. Denial Constraints Tests (`test_denial_constraints.py`)
- **Predicate Logic**: Verifies `is_unary` detection and attribute extraction.
- **String Representation**: Ensures `to_string()` correctly formats constraints for logging and DuckDB queries, including proper quoting of literals.
- **Attribute Extraction**: Validates that `DenialConstraints.attrs` correctly identifies all involved columns.
