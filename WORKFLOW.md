# ICM Workflow Guide: Human-Agent Collaboration

This document defines the operational procedures for the Interpretable Context Methodology (ICM) sandbox and clarifies the roles of the Human (You) and the Agent (Me).

## 1. Collaboration Roles: Who Does What?

The ICM system is designed for **Pair Researching**.

### Your Role (The Researcher)
- **Architectural Decisions**: You decide when to move from one stage to the next.
- **Review & Approval**: You review the `output/` of each stage. If the synthetic data looks "off," you tell me to fix Stage 02.
- **Code Editing (Optional)**: You can edit any `src/` file directly if you have a specific implementation in mind. I will "pick up" your changes in the next turn.
- **Strategic Direction**: You define the parameters for the sweeps in Stage 00.

### My Role (The Agent)
- **Expert Implementation**: I write the boilerplate, the pipeline logic, and the Slurm orchestration based on your high-level instructions.
- **Validation & Testing**: I am responsible for creating and running the notebooks in `tests/` to prove that my code works.
- **Data Management**: I handle the "Handoff" (copying data between stages) and the remote synchronization (Stage 06/07).
- **Error Diagnosis**: If a Slurm job fails, I read the logs and propose the fix.

---

## 2. When to Change Files

| File | Who Changes It? | When? |
| :--- | :--- | :--- |
| **`src/*.py`** | Mostly Agent | When adding/fixing algorithms. |
| **`config/*.yaml`** | Both | When defining new experiment parameters. |
| **`CONTEXT.md`** | Both | When the "contract" between stages changes. |
| **`output/`** | Agent (Write) / Human (Edit) | For manual data cleaning or verification. |

---

## 3. Detailed Workflow Loop

### A. The Local Development Loop (Stages 01-05)
1. **Initialize**: "Agent, I want to add a new repairer to Stage 04."
2. **Implement**: I write the code in `04/src/` and the config in `04/config/`.
3. **Validate**: I run a test notebook in `04/tests/`.
4. **Handoff**: If you approve the test, I copy the `03/output/` to `04/input/` and run the full stage.

### B. The Remote Execution Loop (Stages 00, 06, 07)
1. **Blueprint**: In Stage 00, we generate the 100 experiment folders.
2. **Deploy**: In Stage 06, I push the code to Snorlax and trigger `sbatch`.
3. **Monitor**: You ask "How are my jobs doing?" and I check the queue.
4. **Sync**: Once jobs are done, I pull the results in Stage 07 and aggregate them.

### C. The Analysis Loop (Stage 06)
1. **Explore**: We open a notebook in Stage 06
2. **Visualize**: I write plotting code to show the results of the sweep.
3. **Insight**: I analyze the data and suggest "Epsilon 1.0 is the sweet spot for utility."

---

## 5. Operational Safety (Lessons Learned)

To maintain the integrity of the "Glass Box" and prevent large-scale resource waste, both the Human and the Agent must follow these protocols:

### Mandatory Canary Testing
- **Rule**: NEVER submit a full Slurm array (e.g., 88 jobs) without first running a single "Canary" job (index 1).
- **Procedure**: Run `python s06_remote/src/deploy.py --blueprint [NAME] --canary`. The Agent must then verify the output and error logs before proceeding to the full sweep.

### Verification of Intent
- **Rule**: Before starting a new experiment, the Agent must explicitly summarize the **Scope** (which stages are running) and the **Mode** (e.g., training-only vs. full pipeline).
- **Human Verification**: If the Agent's summary doesn't match your intent (e.g., if you only wanted training and the agent plans evaluation), stop the execution immediately.

### Environment-Agnostic Code
- **Rule**: All `main.py` entry points and orchestrators must use **CWD-Relative Pathing**.
- **Context**: This ensures that code works identically on a local machine and within isolated Slurm temporary workspaces.

### Safe Maintenance
- **Rule**: Avoid bulk destructive edits (e.g., regex shell one-liners). Use surgical, traceable file manipulation tools.

---

## 6. Communication Patterns
... (rest of the file)
