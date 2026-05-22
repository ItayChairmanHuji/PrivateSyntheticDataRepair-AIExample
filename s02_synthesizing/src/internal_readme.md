# Synthesizing Module (Stage 02)

This module provides various differential privacy (DP) data synthesis algorithms and custom violation injection.

## Key Components

### 1. Orchestration (`orchestration/`)
- **`stage_orchestrator.py`**: The central brain. It wires together the input loading, the synthesizer, and the `ArtifactSaver`.

### 2. Infrastructure & I/O (`io/`)
- **`artifact_saver.py`**: Standardized export of synthesis results and carried-over metadata.
- **CLI Tools**: `clean.py` in `cli/`.

### 3. Synthesizers (`components/`)
- **`smart_noise.py`**: Wrapper around `snsynth` (MST, AIM, PATECTGAN).
- **`co_noise.py`**: Custom synthesizer for violation injection.
- **`model_loader.py`**: Loads pre-trained models for sampling.
- **`model_trainer.py`**: Handles training and saving models to `models/`.
- **`synthesizer.py`**: Base abstract class.

## Environment Notes
- Requires `mbi` (from `private-pgm`) and `smartnoise-synth==1.0.5`.
- A reproducibility patch is applied to `mbi` in `main.py`.

## Usage (Python)

```python
from s02_synthesizing.src.components.smart_noise import SmartNoiseSynthesizer

# MST algorithm
synth = SmartNoiseSynthesizer(engine="mst", epsilon=1.0)
# Note: In the pipeline, use the StageOrchestrator for automated I/O.
```
