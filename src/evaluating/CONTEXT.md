# Evaluating

## Goal
The evaluation stage is responsible for quantifying the quality of the synthetic and repaired datasets compared to the private data across multiple dimensions: integrity, utility, and performance.

## Evaluators
1. **Runtime**: Logs the runtime of each part of the pipeline.
2. **Deletion Ratio**: Logs the ratio between the number of tuples after and before the repair.
3. **Marginals Error**: Logs the average error of the obtained marginals for each of the datasets.
4. **2-way TVD**: Computes the averaged Total Variation Distance (TVD) for all 2-way marginals between private data and (synthetic/repaired) data.
5. **ML Accuracy**: The accuracy of machine learning models (Random Forest, Logistic Regression) trained on each dataset and tested on the private dataset.
6. **Violation**: Logs the number of violations in private, synthetic, and repaired datasets.

## Orchestration
The `EvaluationOrchestrator` runs all configured evaluators in sequence and aggregates their results into a single JSON file, ensuring metadata and unique experiment IDs are included.

## Testing
The evaluation system is verified by a suite of tests in `tests/evaluating/`.

### 1. Unit Tests for Evaluators (`test_evaluators.py`)
Uses mocked `PipelineResult` and `Dataset` objects to verify the calculation logic of individual evaluators:
- **`ViolationEvaluator`**: Confirms that it correctly reports violation counts for all three dataset stages.
- **`DeletionRatioEvaluator`**: Validates the ratio calculation based on tuple counts before and after repair.
- **`TwoWayTVDEvaluator`**: Ensures that TVD is calculated correctly for pairs of attributes.
- **`RuntimeEvaluator`**: Verifies that it correctly extracts and formats runtime metadata.
- **`MarginalsErrorEvaluator`**: Validates the error calculation between obtained marginals and the resulting datasets.

### 2. Orchestration Tests (`test_orchestrator.py`)
Tests the `EvaluationOrchestrator` to ensure proper integration:
- **Result Aggregation**: Confirms that metrics from multiple evaluators are correctly combined into a single result dictionary.
- **File System Interaction**: Verifies that results are successfully saved as JSON files in the specified directory structure, including experiment-specific subdirectories.
- **Collision Safety**: Ensures that unique filenames (using experiment IDs) are generated to prevent overwriting results from concurrent or sequential runs.

