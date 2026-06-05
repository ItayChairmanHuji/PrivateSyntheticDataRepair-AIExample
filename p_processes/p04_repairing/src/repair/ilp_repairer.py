from dataclasses import dataclass, field
from typing import Any
import gurobipy as gp
from u_utilities.u_shared.dataset import Dataset
from u_utilities.u_shared.marginal import MarginalSet
from old.s04_repairing.src.repair.repairer import Repairer
from old.shared.utils.gurobi_helper import GurobiHelper

@dataclass
class ILPRepairer(Repairer):
    """
    Implements the ILP repair formulation using Gurobi.
    """
    alpha: float
    gurobi_params: dict = field(default_factory=dict)
    use_marginals: bool = True

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        model = self._setup_model()
        n = len(dataset.data)
        x = model.addVars(n, vtype=gp.GRB.BINARY, name="x")
        
        self._add_conflict_constraints(model, x, dataset)
        
        if self.use_marginals and marginals:
            self._add_marginal_objective(model, x, n, marginals, dataset)
        else:
            self._add_simple_objective(model, x, n)

        model.optimize()
        return self._create_output_dataset(model, x, dataset)

    def _setup_model(self) -> gp.Model:
        env = GurobiHelper.get_env()
        model = gp.Model("ILP_Repair", env=env)
        for param, value in self.gurobi_params.items():
            model.setParam(param, value)
        return model

    def _add_conflict_constraints(self, model, x, dataset):
        violations = dataset.get_violations()
        for b in violations.bicliques:
            for idx1 in b.left_nodes:
                for idx2 in b.right_nodes:
                    model.addConstr(x[int(idx1)] + x[int(idx2)] <= 1)

    def _add_marginal_objective(self, model, x, n, marginals, dataset):
        m_len = len(marginals)
        d = model.addVars(m_len, vtype=gp.GRB.CONTINUOUS, lb=0, name="d")
        N = gp.quicksum(x[i] for i in range(n))
        model.setParam("NonConvex", 2)

        for i, m in enumerate(marginals):
            matching_indices = dataset.data[m.get_mask(dataset.data)].index.tolist()
            C_m = gp.quicksum(x[idx] for idx in matching_indices)
            model.addConstr(d[i] * N >= C_m - m.target * N)
            model.addConstr(d[i] * N >= m.target * N - C_m)

        removal_loss = (n - N) / n
        marginal_loss = gp.quicksum(d[i] for i in range(m_len)) / m_len
        model.setObjective(self.alpha * removal_loss + (1 - self.alpha) * marginal_loss, gp.GRB.MINIMIZE)

    def _add_simple_objective(self, model, x, n):
        model.setObjective((n - gp.quicksum(x[i] for i in range(n))) / n, gp.GRB.MINIMIZE)

    def _create_output_dataset(self, model, x, dataset) -> Dataset:
        if model.status == gp.GRB.OPTIMAL:
            keep_indices = [i for i in range(len(dataset.data)) if x[i].X > 0.5]
            data = dataset.data.iloc[keep_indices].reset_index(drop=True)
        else:
            data = dataset.data.drop(index=dataset.data.index)
        
        return Dataset(name=f"{dataset.name}_repaired", data=data, dcs=dataset.dcs, target=dataset.target)
