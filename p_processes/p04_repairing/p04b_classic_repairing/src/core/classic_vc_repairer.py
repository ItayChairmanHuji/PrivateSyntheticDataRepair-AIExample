import random
from dataclasses import dataclass

from p_processes.p04_repairing.src.core import Graph, Repairer
from u_utilities.u_shared import Dataset, MarginalSet


@dataclass
class ClassicVCRepairer(Repairer):
    alpha: float = 0.5

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        violations = dataset.get_violations()
        n_rows = len(dataset.data)

        graph = Graph(n_rows, violations)

        removed = set()
        while graph.ecount() > 0:
            active_nodes = graph.vs.select(_degree_gt=0)
            selected = int(random.choice(active_nodes))
            removed.add(selected)
            graph.delete_edges(selected)

        keep_indices = [i for i in range(n_rows) if i not in removed]
        data = dataset.data.iloc[keep_indices].reset_index(drop=True)

        return Dataset(
            name=f"{dataset.name}_repaired",
            data=data,
            dcs=dataset.dcs,
            target=dataset.target,
        )
