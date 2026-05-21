# Stage 00: Experiment Design

## Purpose
Translate high-level research questions into concrete experiment configurations and folder structures ("Blueprints").

## Contract
**Inputs (Layer 3 - `config/`):**
- Master sweep templates (Hydra YAMLs).
- Parameter ranges (alpha, epsilon, dataset names).

**Process:**
- Logic in `src/` iterates through parameter combinations.
- Generates a `blueprint.json` or a set of stage-specific YAMLs.
- (Optional) Creates the physical folder structure for the sweep if running locally.

**Outputs (Layer 4 - `output/`):**
- Experiment Blueprint: A self-contained set of configs for all jobs in the sweep.
- Slurm `sbatch` scripts or job array definitions.

## Stage Rules
- A Blueprint must be immutable once generated for a specific run.
- Always include a `metadata.json` describing the intent of the sweep.
