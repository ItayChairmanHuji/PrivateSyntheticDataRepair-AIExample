import random
from dataclasses import dataclass

import numpy as np

from p_processes.p04_repairing.src.core import ConflictGraphBuilder, Repairer
from u_utilities.u_shared import Dataset, MarginalSet


@dataclass
class ClassicVCRepairer(Repairer):
    alpha: float = 0.5

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        violations = dataset.get_violations()
        n_rows = len(dataset.data)

        graph = ConflictGraphBuilder.build(n_rows, violations)

        removed = set()
        while graph.has_edges():
            u, v = graph.pick_random_edge()
            selected = random.choice([u, v])
            removed.add(selected)
            graph.remove_vertex(selected)

        keep_indices = [i for i in range(n_rows) if i not in removed]
        data = dataset.data.iloc[keep_indices].reset_index(drop=True)

        return Dataset(
            name=f"{dataset.name}_repaired",
            data=data,
            dcs=dataset.dcs,
            target=dataset.target,
        )
