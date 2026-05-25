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

## Workflow
1.  **Draft**: Create a new experiment file in `experiments/` (e.g., `experiment_1.md`).
2.  **Plan**: Define a template in `templates/`.
3.  **Generate**: Run `src/generate_blueprint.py` to create a blueprint in `blueprints/`.
4.  **Track**: Update the status in the experiment file as it moves through stages.
5.  **Rerun**: If a bug is found, fix it locally and use `remote` utilities to rerun the experiment (which handles cleaning remote state).
6.  **Journal**: Record significant milestones and daily progress in the `journal/`.
