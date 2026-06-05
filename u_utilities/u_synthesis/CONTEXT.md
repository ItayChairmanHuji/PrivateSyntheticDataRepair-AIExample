# Utility: u_synthesis

## Purpose
Core generation algorithms and model wrappers.

## Interface
- **`SmartNoiseSynthesizer`**: Wrapper for SmartNoise-SQL / DPSyn.
- **`CoNoiseSynthesizer`**: Correlated noise addition for small-domain data.

## Usage
```python
from u_utilities.u_synthesis import SmartNoiseSynthesizer
synth = SmartNoiseSynthesizer(epsilon=1.0)
synth.fit(data)
synthetic_df = synth.sample(10000)
```
