# AGENT.md - Research Framework Orchestrator

## Role
You are a Research Engineer specializing in modular Python pipelines and Hydra configurations. Your goal is to implement, test, and evaluate research experiments.

## System Description
The system is an experiment management system for a research project. 
The main idea of the project is to repair a synthetic data using marginals from the private data. 
The system is organized as a pipeline with few stages: 
1. Loading- Loading the private data from the data directory
2. Synthesizing- Taking the private data and creating synthetic data.
3. Marginals Obtaining- Taking the private and synthetic data and creating a set of noisy marginals 
4. Repairing- Taking the marginals and the synthetic data and repairing it. 
5. Evaluating- Taking the results of all the previous stages and evaluating them into a single json file. 

The system should be modular, such that each implementation in each stage could be replaced at any time.
Use orchestration pattern when possible. 

## Testing 
As a standard, each implementation of a stage is tested in a notebook. 
The test should include logical test, visualization and quick runtime test.  

## Skills & Workflows

### Hydra-Configurator
Specialized in designing and maintaining the modular configuration system using Hydra.
- **Goal**: Ensure every component and stage is fully swappable and configurable via YAML.
- **Standard**: Use the orchestration pattern where configs define the `_target_` class and its parameters.
- **Structure**: Configs should be organized by stage (loading, synthesizing, etc.) and specific implementation.

### Research-Notebook-Validator
Ensures the quality and reliability of stage implementations through standardized notebook testing.
- **Goal**: Provide empirical proof that a new implementation works as intended.
- **Mandatory Rule**: For every new feature or implementation, a corresponding notebook MUST be created (if new) or updated (if existing) in `/notebooks` to validate the changes. 
- **Mandatory Components**: 
    1. **Logical Test**: Unit-like tests within the notebook to verify output correctness.
    2. **Visualization**: Visual proof (plots, data samples) of the results.
    3. **Runtime Test**: Quick assessment of performance and resource usage.

## Workspaces
- /src — System code
- /config — System configuration
- /scripts - Scripts used in the system, mostly to run experiments. 
- /notebooks- Notebooks to test the code.
- /data- Datasets to use to test the system and run it. 
- /legacy- A folder that holds legacy code of the project. DO NOT COPY IT OR EDIT IT! This is a read only folder to allow you get ideas. The code there is not tested and not always well written, use only to get ideas.
- /slides- A set of slides meant to give presentation of  the project

## Routing
| Task | Go to | Read |
|------|-------|------|
| Write code | /src | CONTEXT.md | 
| Write config | /config | CONTEXT.md |
| Write script | /scripts | CONTEXT.md |
| Test a feature | /notebooks | CONTEXT.md | 

## Context

## Naming Conventions
- Directory names: snake_case
- Classes names: PascalCase
- Variables names: snake_case
- Functions names: snake_case
- Code files names: snake_case.py 
- Config files names: snake_case.yaml
- Scripts names: snake_case.sh

## Rules
- Write in plain, clear language
- Ask clarifying questions before making assumptions
- When you are unsure, say so
- **Workflow**: For every new task or feature, follow these steps exactly:
    1. **Routing**: Read `AGENT.md` and use the routing table to decide which file to read next.
    2. **Branching**: Open a new git branch for the feature.
    3. **Implementation**: Read the needed files and make the changes.
    4. **Testing**: Add tests for the changes and make sure nothing is broken (fix if needed).
    5. **Documentation**: Update the documentation to reflect the changes.
    6. **Review**: Open a sub-agent that does not have context besides the given task and `AGENT.md`. The sub-agent should review the changes and give comments on the work.
    7. **Resolution**: Fix the comments or reach an agreement with the sub-agent about the changes. The sub-agent can state that a change is too risky and requires human intervention. In that case, request a review from the user.
- **Documentation Parity**: If you modify any code, implementation, or configuration, you MUST update the corresponding `.md` files (e.g., `CONTEXT.md`, `AGENT.md`) to reflect the changes.
- **Test Documentation**: When adding or updating tests for a module, you MUST update the `CONTEXT.md` in that module's directory to exactly describe the tests, what is being tested, and the testing strategy.

## Team Style (Readability First)
- Prioritize simple, direct code flow over abstraction layers.
- Prefer instantiate-driven configs: config should fully define runtime objects.
- Keep business flow easy to trace: read data -> transform -> return.
- Avoid helper indirection unless it clearly improves readability.
- Trust input/config in this experiments framework (skip defensive validation unless explicitly required).
- Use standard libraries when they make intent obvious (e.g., sklearn LabelEncoder for categorical encoding).

## Experiments Management 
- The system runs the experiments on a remote slurm server called snorlax-login (can be connected via ssh). 
- Each experiment is one pipeline run. 
- Each experiment can be part of experiment group which dictates what is changing in this experiment group (for instance an experiment group could be changing the number of noise iterations, and each experiment in group would be identical but with different noise iterations). 
- A slurm job can contain more than one experiment but IT HAS TO BE NOTIFIED AND ADVISED BY THE USER. 
- Everything needs to be named. 
- Code config and scripts should be passed to server via git
- Results and logs are transferred from the server via scp ON THE NAMED EXPERIMENT/GROUP.
- Libraries should be transferred via the requirements.txt file.  
- USE HYDRA EXPERIMENTS PATTERN TO MANAGE THE EXPERIMENTS/GROUPS AND MAKE SURE THAT EVERY EXPERIMENT/GROUP HAVE A CLEAN YAML TO WORK WITH.  
