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

### C. The Analysis Loop (Stage 08)
1. **Explore**: We open a notebook in Stage 08.
2. **Visualize**: I write plotting code to show the results of the sweep.
3. **Insight**: I analyze the data and suggest "Epsilon 1.0 is the sweet spot for utility."

---

## 4. Communication Patterns

- **"Execute Stage X"**: Tells me to run the `main.py` for that stage using the current `input/`.
- **"What's the status of X?"**: Tells me to look at the `output/` or `logs/` of a stage and summarize the state.
- **"Activate Skill [Name]"**: Brings the specialized procedural knowledge for that stage into my active memory.
