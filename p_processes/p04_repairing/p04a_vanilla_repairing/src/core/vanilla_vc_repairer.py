from dataclasses import dataclass

import numpy as np

from p_processes.p04_repairing.src.core import Repairer, ConflictGraphBuilder
from u_utilities.u_shared import Dataset, MarginalSet


@dataclass
class VanillaVCRepairer(Repairer):
    alpha: float = 0.5

    def repair(self, dataset: Dataset, marginals: MarginalSet) -> Dataset:
        violations = dataset.get_violations()
        n_rows = len(dataset.data)

        graph = ConflictGraphBuilder.build(n_rows, violations)

        removed = set()
        while graph.ecount() > 0:
            degrees = graph.degree()
            selected = int(np.argmax(degrees))
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
