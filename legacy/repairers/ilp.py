import json
from dataclasses import dataclass

import gurobipy as gp

from entities.dataset import Dataset
from marginals.marginal import Marginal


def setup_env(gp_license: dict):
    env = gp.Env(params=gp_license)
    env.setParam("OutputFlag", True)
    env.setParam("MIPGap", 0)
    env.setParam("MIPGapAbs", 0)
    env.setParam("TimeLimit", 7200)
    return env


@dataclass
class ILPRepairer:
    license_path: str
    alpha: float

    def repair(self, data: Dataset, marginals: list[Marginal]):
        env = setup_env(json.load(open(self.license_path)))
        model = gp.Model("ILP_Repair", env=env)
        x = model.addVars(range(len(data)), vtype=gp.GRB.BINARY)
        d = model.addVars(range(len(marginals)), vtype=gp.GRB.CONTINUOUS, lb=0)
        self._create_optimization(model, x, d, data, marginals)
        self._create_constraints(model, x, d, data, marginals)
        model.optimize()
        return x, d

    @staticmethod
    def _analyze_solution(model: gp.Model) -> list[int]:
        objective = model.getVars()
        if model.status == gp.GRB.INFEASIBLE:
            return list(range(len(objective)))
        return [i for i in range(len(objective)) if objective[i].X < 0.5]

    def _create_optimization(self, model, x, d, data, marginals):
        loss = self._loss(x, d, data, marginals)
        model.setObjective(loss, gp.GRB.MINIMIZE)

    def _create_constraints(self, model, x, d, data, marginals):
        dcs_constraint = self._dcs_violations_constraint(data, x)
        model.addConstrs(dcs_constraint)

        marginals_constraint = self._marginals_constraint(data, marginals, x, d)
        model.addConstrs(marginals_constraint)

    def _loss(self, x, d, data, marginals):
        size_loss = self._repair_size_loss(x, data)
        marg_loss = self._repair_marginal_loss(d, marginals)
        return self.alpha * size_loss + (1 - self.alpha) * marg_loss

    def _repair_size_loss(self, x, data):
        return (len(data) - x.sum()) / len(data)

    def _repair_marginal_loss(self, d, marginals):
        return (d.sum()) / len(marginals)

    def _dcs_violations_constraint(self, data: Dataset, x):
        return [x[pair[0]] + x[pair[1]] <= 1 for pair in data.dcs_violations]

    def _marginals_constraint(self, data: Dataset, marginals: list[Marginal], x, d):
        res = []
        for m_index, marginal in enumerate(marginals):
            indices = marginal.indices(data.data)
            size = 1 / len(data) * x[indices].sum()
            res.append(d[m_index] >= size - marginal.target)
            res.append(d[m_index] >= marginal.target - size)
        return res
