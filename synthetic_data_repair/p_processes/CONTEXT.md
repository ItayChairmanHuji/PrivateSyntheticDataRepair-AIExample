# Processes (p_processes)

## Purpose
Processes are the functional units that transform resources. They represent the "Verbs" of the framework (e.g., Load, Train, Repair).

## Design Principles
1. **Granularity:** Processes are small and single-purpose (e.g., `p02a_training`).
2. **Hydra-Native:** All processes use `@hydra.main` and support CLI overrides and sweeps.
3. **No Local State:** Processes do not have `input/` or `output/` folders. They interact directly with `r_resources`.
4. **Thin Wrappers:** Logic resides in `u_utilities`; processes handle the orchestration and CLI interface.

## Standard Execution
To run a process:
```bash
python -m p_processes.p02a_training.main dataset_name=adult100 epsilon=0.1
```

To run a sweep:
```bash
python -m p_processes.p02a_training.main --multirun epsilon=0.1,0.5,1.0
```
