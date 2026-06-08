from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from p_processes.p04_repairing.src.core.graph.block_pair import BlockMembership, BlockPair


@dataclass
class Graph:
    n: int
    degrees: np.ndarray
    active: np.ndarray
    deleted: np.ndarray
    block_pairs: list[BlockPair]
    cluster_to_blocks: list[list[BlockMembership]]
    row_to_cluster: np.ndarray

    def has_edges(self) -> bool:
        return bool(self.active.any())

    def degree(self, indices: np.ndarray) -> np.ndarray:
        return self.degrees[indices]

    def remove_vertex(self, row_idx: int) -> None:
        if self.deleted[row_idx] or not self.active[row_idx]:
            return

        self._update_neighbors(row_idx)
        self.deleted[row_idx] = True
        self.active[row_idx] = False
        self.degrees[row_idx] = 0

    def pick_random_edge(self) -> tuple[int, int]:
        active_indices = np.where(self.degrees > 0)[0]
        if len(active_indices) == 0:
            raise ValueError("No edges left in graph")

        # Select a random active vertex weighted by its degree
        u = int(np.random.choice(active_indices, p=self.degrees[active_indices] / self.degrees.sum()))
        
        # Find a random neighbor v of u
        c_id = self.row_to_cluster[u]
        active_memberships = [m for m in self.cluster_to_blocks[c_id] if m.affected_members(self.block_pairs[m.block_pair_idx]).any()]
        membership = np.random.choice(active_memberships)
        block = self.block_pairs[membership.block_pair_idx]
        
        neighbors = membership.affected_members(block)
        active_neighbors = neighbors[self.active[neighbors] & (neighbors != u)]
        v = int(np.random.choice(active_neighbors))
        
        return u, v

    def _update_neighbors(self, row_idx: int) -> None:
        c_id = self.row_to_cluster[row_idx]
        if c_id >= 0:
            for membership in self.cluster_to_blocks[c_id]:
                block = self.block_pairs[membership.block_pair_idx]
                neighbors = membership.affected_members(block)

                # Filter active neighbors and batch decrement
                active_neighbors = neighbors[self.active[neighbors]]
                if len(active_neighbors) > 0:
                    self.degrees[active_neighbors] -= 1
                    self.active[active_neighbors] = self.degrees[active_neighbors] > 0
