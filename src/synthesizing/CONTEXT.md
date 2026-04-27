# Synthesizing 

## Goal
The synthesizing stage is responsible for creating a synthetic version of the private dataset. This synthetic data often serves as a baseline that may contain integrity violations which need to be repaired.

## Synthesizers 
1. **Synthesizer**: Abstract base class for all synthetic data generation strategies. 
2. **Co-Noise**: An algorithm designed to systematically introduce integrity violations into a dataset. It "breaks" denial constraints by modifying random pairs of tuples.
3. **Smart-Noise** (Planned): Integration with the SmartNoise library for DP-synthetic data.
4. **Kamino** (Planned): Integration with the Kamino algorithm.

### Co-Noise Algorithm
For a specified number of iterations:
1. Randomly select a constraint $\sigma$ from the set $\Sigma$.
2. Randomly select two tuples $t_i$ and $t_j$.
3. For every predicate $\phi$ in $\sigma$:
   - If $\phi$ is already satisfied, continue.
   - If the operator is $\{=, \leq, \geq\}$, force equality or boundary satisfaction by modifying one of the tuples.
   - If the operator is $\{<, >, \neq\}$, modify one of the tuples using values from the active domain (or a generated value) to ensure satisfaction.

## Testing
The synthesizing system is verified by tests in `tests/synthesizing/`.

### 1. Co-Noise Tests (`test_co_noise.py`)
Validates the behavior and reliability of the `CoNoise` synthesizer:
- **Violation Introduction**: Confirms that running Co-Noise on a violation-free dataset successfully introduces conflicts that are detectable by the `ViolationFinder`.
- **Data Integrity**: Ensures that the synthesis process preserves the shape (rows and columns) of the original dataset.
- **Reproducibility**: Verifies that providing a fixed seed results in deterministic output, which is critical for experimental consistency.
- **Edge Cases**: Validates that the synthesizer handles datasets with no denial constraints by returning the data unchanged.


