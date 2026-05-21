# Synthesizing Module

This module provides various differential privacy (DP) data synthesis algorithms.

## Key Components

### SmartNoiseSynthesizer
- **File**: `smart_noise.py`
- **Description**: A wrapper around the `snsynth` library.
- **Supported Engines**: `mst`, `aim`, `patectgan`.
- **Environment Notes**: Requires `mbi` (from `private-pgm`) and `smartnoise-synth==1.0.5`.

### CoNoiseSynthesizer
- **File**: `co_noise.py`
- **Description**: A custom synthesizer that incorporates denial constraints during noise generation.

## Testing

- **SmartNoise**: `tests/synthesizing/test_smart_noise.py`
- **Co-Noise**: `tests/synthesizing/test_co_noise.py`

## Usage

```python
from src.synthesizing.smart_noise import SmartNoiseSynthesizer

# MST algorithm
synth = SmartNoiseSynthesizer(engine="mst", epsilon=1.0)
result = synth.synthesize(dataset)

# PATECTGAN with custom epochs
synth = SmartNoiseSynthesizer(engine="patectgan", epsilon=1.0, epochs=20)
result = synth.synthesize(dataset)
```
