# Mission Control Example: Alpha Sweep

This example demonstrates how to use Mission Control to plan and track a parameter sweep over `alpha` (repair strength).

## 1. Documentation (The Registry)
Before writing code or configs, you start by documenting the intent.

**File: `experiments/alpha_sweep_journal.md`**
```markdown
# Alpha Sweep: Repair Strength Sensitivity

## Hypothesis
Increasing alpha (vertex cover weight) will improve data utility but might increase bias in specific marginals.

## Parameters
- Datasets: Adult
- Epsilon: 1.0
- Alpha: [0.0, 0.25, 0.5, 0.75, 1.0]

## Status
- [x] Planning
- [ ] Blueprint Generated
- [ ] Stage 01 (Loading)
- [ ] Stage 02 (Synthesizing)
- ...
```

## 2. Planning (The Template)
Create a master template in `templates/` that defines the sweep logic.

**File: `templates/alpha_sweep.yaml`**
```yaml
experiment_group: alpha_sweep_may2026
base_config:
  dataset: adult
  epsilon: 1.0
  synthesizer: aim

sweep_parameters:
  repairing.alpha: [0.0, 0.25, 0.5, 0.75, 1.0]
  seed: [42, 43, 44]
```

## 3. Freezing (The Blueprint)
Run the generator to lock in the execution plan.

**Command:**
```powershell
python mission_control/src/generate_blueprint.py --template mission_control/templates/alpha_sweep.yaml
```

**Resulting Blueprint:** `mission_control/blueprints/alpha_sweep_may2026/blueprint.json`

## 4. Execution & Tracking
As the pipeline runs, you update the `Status` section in `experiments/alpha_sweep_journal.md`. This ensures you (and I) always know the exact state of the research.

## Why this is a "Control Center":
- **Single Source of Truth**: The experiment file in `experiments/` is the master record.
- **Traceability**: You can trace any result back to a specific Blueprint and Template.
- **Safety**: Blueprints are immutable. If you need to change a parameter, you create a *new* experiment entry.
