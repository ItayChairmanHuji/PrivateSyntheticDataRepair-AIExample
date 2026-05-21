# Experiment 1: Model Generation Sweep

## Goal 
Generate a comprehensive set of models (AIM, MST) across a range of privacy budgets (epsilon) for Adult, Census, Compas, and Tax datasets.

## Parameters 
- **Datasets**: Adult, Census, Compas, Tax
- **Synthesizers**: AIM, MST
- **Epsilon Sweep**: 0.001, 0.1, 0.2, ..., 1.0 (11 values)
- **Seeds**: 1 (Assuming 1 seed per configuration for this initial generation)

## Registry
- **Template**: `mission_control/templates/experiment_1_template.yaml`
- **Blueprint**: `mission_control/blueprints/experiment_1_generation/blueprint.json`
- **Output Artifacts**: `outputs/experiment_1_generation`

## Status
- [x] **Planning**: Defined goals and parameters.
- [x] **Blueprint Generated**: 88 jobs defined (4 datasets * 2 synthesizers * 11 eps values).
- [/] **Stage 01 (Loading)**: verified.
- [/] **Stage 02 (Synthesizing)**: verified.
- [ ] **Stage 03 (Marginals)**: Pending
- [/] **Stage 05 (Evaluating)**: Pending
- [/] **Remote Execution (Stage 06)**: Done.