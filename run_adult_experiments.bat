@echo off
echo Running full Adult experiments...

set "data=adult"

echo --- Running ILP (With Marginals) ---
python main.py loading.name=%data% repairing=ilp experiment_name=adult_full_ilp_marginals repairing.use_marginals=True synthesizing.num_of_iterations=50

echo --- Running ILP (No Marginals) ---
python main.py loading.name=%data% repairing=ilp experiment_name=adult_full_ilp_no_marginals repairing.use_marginals=False synthesizing.num_of_iterations=50

echo --- Running Classic VC ---
python main.py loading.name=%data% repairing=classic_vc experiment_name=adult_full_classic_vc synthesizing.num_of_iterations=50

echo --- Running Vanilla VC ---
python main.py loading.name=%data% repairing=vanilla_vc experiment_name=adult_full_vanilla_vc synthesizing.num_of_iterations=50

echo --- Running Weighted VC ---
python main.py loading.name=%data% repairing=weighted_vc experiment_name=adult_full_weighted_vc synthesizing.num_of_iterations=50

echo --- Collecting Results ---
python scripts/collect_results_full.py