# Experiment 9: PATE-CTGAN Training Sweep

## Goal
Train PATE-CTGAN models for datasets `adult`, `census`, `compas`, and `tax` across a range of epsilon values to populate the `models/` directory and evaluate baseline performance.

## Configuration
- **Synthesizer**: `patectgan` (using `SmartNoiseModelTrainer`)
- **Datasets**: `adult`, `census`, `compas`, `tax`
- **Epsilon Sweep**: `[0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]`
- **Repair Algorithm**: `vanilla_vc` (Baseline)
- **Seeds**: `[42]` (Initial training)
- **Mode**: `full` (Train + Sample + Eval)

## Status
- [x] Template created: `mission_control/templates/experiment_9_patectgan_sweep.yaml`
- [x] Config created: `s02_synthesizing/config/patectgan_trainer.yaml`
- [x] Blueprint generated: `mission_control/blueprints/experiment_9_patectgan_sweep`
- [x] Blueprint synced to `remote/input/`
- [ ] Deployed to remote cluster

## Jobs
Total jobs: 44 (4 datasets * 11 epsilons)
Blueprint: `experiment_9_patectgan_sweep`
