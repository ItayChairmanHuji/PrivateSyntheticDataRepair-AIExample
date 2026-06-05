# Mission Control

Mission Control is the planning and registry hub for the research framework. It tracks what experiments are running, what was learned, and what needs to be done next.

## Structure
- `journal/`: Daily notes, brain dumps, and unstructured observations.
- `experiments/`: Structured Markdown files detailing the hypothesis, parameters, and results of specific experimental sweeps.

## Workflow
1. Write a new experiment plan in `experiments/`.
2. Generate the corresponding Hydra configuration in `r_resources/r_configs/experiments/`.
3. Update the registry in `CONTEXT.md` as the experiment progresses.

For more details on rules and AI interaction, see [CONTEXT.md](CONTEXT.md).
