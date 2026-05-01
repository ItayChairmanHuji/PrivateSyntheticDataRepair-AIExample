import gurobipy as gp
import pandas as pd
from dataclasses import dataclass, field
from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet
from src.repairing.repairer import Repairer

from src.utils.gurobi_helper import GurobiHelper

@dataclass
class ILPRepairer(Repairer):
    """
    Implements the ILP repair formulation using Gurobi.
    """
    alpha: float
    gurobi_params: dict = field(default_factory=dict)
    use_marginals: bool = True

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        # Create a model with the licensed environment
        env = GurobiHelper.get_env()
        model = gp.Model("ILP_Repair", env=env)
        
        # Set Gurobi parameters
        for param, value in self.gurobi_params.items():
            model.setParam(param, value)

        n = len(dataset.data)
        
        # Binary variables: x_l = 1 if tuple t_l is KEPT, 0 if REMOVED
        x = model.addVars(n, vtype=gp.GRB.BINARY, name="x")
        
        # 1. Conflict Constraints: x_i + x_j <= 1 for all conflicting tuples
        violations = dataset.get_violations()
            
        for _, row in violations.iterrows():
            idx1, idx2 = int(row['idx1']), int(row['idx2'])
            model.addConstr(x[idx1] + x[idx2] <= 1, name=f"conflict_{idx1}_{idx2}")

        # 2. Objective and Marginal Constraints
        if self.use_marginals and marginals and len(marginals) > 0:
            m_len = len(marginals)
            # Continuous variables for absolute differences d_m
            d = model.addVars(m_len, vtype=gp.GRB.CONTINUOUS, lb=0, name="d")
            
            # Total kept tuples N
            N = gp.quicksum(x[i] for i in range(n))
            
            # Enable NonConvex parameter for quadratic constraints (d_m * N)
            model.setParam('NonConvex', 2)
            
            for i, m in enumerate(marginals):
                # Mask for tuples matching the marginal's values
                matching_indices = dataset.data[m.get_mask(dataset.data)].index.tolist()
                
                # count of kept tuples matching the marginal
                C_m = gp.quicksum(x[idx] for idx in matching_indices)
                
                # d_m * N >= C_m - target * N AND d_m * N >= target * N - C_m
                model.addConstr(d[i] * N >= C_m - m.target * N, name=f"marg_pos_{i}")
                model.addConstr(d[i] * N >= m.target * N - C_m, name=f"marg_neg_{i}")
            
            # Minimize alpha * (n - N)/n + (1-alpha) * sum(d)/|M|
            removal_loss = (n - N) / n
            marginal_loss = gp.quicksum(d[i] for i in range(m_len)) / m_len
            model.setObjective(self.alpha * removal_loss + (1 - self.alpha) * marginal_loss, gp.GRB.MINIMIZE)
        else:
            # If ignoring marginals, just minimize the number of removed tuples (maximize sum(x))
            model.setObjective((n - gp.quicksum(x[i] for i in range(n))) / n, gp.GRB.MINIMIZE)

        # 3. Solve
        model.optimize()

        # 4. Filter the data
        if model.status == gp.GRB.OPTIMAL or model.status == gp.GRB.TIME_LIMIT:
            keep_indices = [i for i in range(n) if x[i].X > 0.5]
            repaired_data = dataset.data.iloc[keep_indices].reset_index(drop=True)
            
            return Dataset(
                name=f"{dataset.name}_repaired",
                data=repaired_data,
                dcs=dataset.dcs,
                target=dataset.target
            )
        else:
            # If infeasible or error, return the original data
            return Dataset(
                name=dataset.name,
                data=dataset.data,
                dcs=dataset.dcs,
                target=dataset.target
            )
