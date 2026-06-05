# Processes (`p_processes`)

This directory contains the functional entry points for the RPM architecture. Think of these as the "Verbs" of the framework.

## Design
- **Granular:** Each folder (e.g., `p01_loading`, `p02a_training`) represents a single, atomic step in the pipeline.
- **Stateless:** Processes do not have local `input/` or `output/` folders. They interact directly with `r_resources`.
- **Hydra-Native:** Execution is driven by Hydra configurations, allowing for easy overrides and parameter sweeps.

## Usage
Processes are executed as Python modules. For example:
```bash
python -m p_processes.p02a_training.main dataset_name=adult100 epsilon=0.1
```

For more details on rules and AI interaction, see [CONTEXT.md](CONTEXT.md).
