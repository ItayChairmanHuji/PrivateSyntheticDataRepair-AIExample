# Mission Control

## Purpose
The central hub for experiment planning, tracking, and management. It serves as the "Glass Box" control center where the high-level research intent is translated into execution and documented.

## Responsibilities
- **Planning**: Defining experiment sweeps and configurations.
- **Registry**: Maintaining a record of all experiments and their current status.
- **Templates**: Storing baseline configurations for datasets and models.
- **Blueprints**: Generating immutable execution plans for the pipeline stages.
- **Logbook**: Tracking the overall progress of the research project.

## Structure
- `templates/`: YAML templates for experiment sweeps.
- `blueprints/`: Generated JSON/YAML configs for specific runs.
- `experiments/`: Markdown files documenting each individual experiment (e.g., `exp_001.md`).
- `src/`: Utility scripts for generating blueprints and managing the registry.
- `journal/`: A daily record of research activities and decisions.

## Agent Guardrails
To ensure the integrity of the research framework and the reproducibility of experiments, agents MUST adhere to the following rules:
- **Isolation of Stages**: Avoid modifying code or default configuration files (e.g., `sXX_stage/config/stage.yaml`) in individual stages. These are baseline components and should remain stable.
- **Config Overrides First**: If an experiment requires a change in behavior or parameters, ALWAYS prefer overriding the values in the experiment template (`mission_control/templates/`) or the generated blueprint. 
- **Code Stability**: Only modify stage code if a bug is identified that affects all experiments. For experiment-specific logic, use conditional parameters passed via the orchestrator.
- **Blueprint Integrity**: Never modify a blueprint in `blueprints/` manually. If the plan needs to change, update the template and regenerate the blueprint.

## Workflow
1.  **Draft**: Create a new experiment file in `experiments/` (e.g., `experiment_1.md`).
2.  **Plan**: Define a template in `templates/`.
3.  **Generate**: Run `src/generate_blueprint.py` to create a blueprint in `blueprints/`.
4.  **Track**: Update the status in the experiment file as it moves through stages.
5.  **Rerun**: If a bug is found, fix it locally and use `remote` utilities to rerun the experiment (which handles cleaning remote state).
6.  **Journal**: Record significant milestones and daily progress in the `journal/`.
