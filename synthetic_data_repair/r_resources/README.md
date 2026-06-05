# Resources (`r_resources`)

This directory is the single source of truth for all persistent state in the framework, including datasets, models, configurations, and results.

## The Parameter Identity Rule
Paths within `r_resources` are not arbitrary. They are strictly calculated based on the parameters that define the resource (e.g., `synth/eps/seed/size/data.csv`). 

**Never manipulate files in this directory manually.** All read/write operations must be performed programmatically via the `ResourceManager` located in `u_utilities/u_io`.

## Structure
- `r_configs/`: Hydra configuration files (Base and Experiments).
- `r_data/`: Cleaned and synthetic datasets.
- `r_models/`: Trained synthesizer models.
- `r_results/`: Evaluation metrics and reports.

For more details on rules and AI interaction, see [CONTEXT.md](CONTEXT.md).
