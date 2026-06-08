from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ClusterMap:
    row_to_cluster: np.ndarray
    members: list[np.ndarray]

    @classmethod
    def empty(cls, n: int) -> ClusterMap:
        return cls(np.full(n, -1, dtype=int), [])

    @classmethod
    def from_parts(
        cls, n: int, row_to_cluster: np.ndarray | None, members: list[np.ndarray] | None
    ) -> ClusterMap:
        if row_to_cluster is None:
            return cls.empty(n)
        return cls(row_to_cluster, members or [])

    def cluster_of(self, row_idx: int) -> int:
        return int(self.row_to_cluster[row_idx])

    def members_for(self, cluster_ids: np.ndarray) -> np.ndarray:
        if len(cluster_ids) == 0:
            return np.array([], dtype=int)
        if len(cluster_ids) == 1:
            return self.members[int(cluster_ids[0])]
        return np.concatenate([self.members[int(cid)] for cid in cluster_ids])

    def count_members(self, cluster_ids: np.ndarray) -> int:
        return int(sum(len(self.members[int(cid)]) for cid in cluster_ids))
