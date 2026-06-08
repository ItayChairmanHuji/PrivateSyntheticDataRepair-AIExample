from __future__ import annotations

import numpy as np

from p_processes.p04_repairing.src.core.graph.graph import Graph
from u_utilities.u_shared import ViolationSet

from .block_pair import BlockMembership, BlockPair, BlockSide
from .cluster_map import ClusterMap


class GraphBuilder:
    def __init__(self, n: int, violation_set: ViolationSet) -> None:
        self.n = n
        self.cluster_map = ClusterMap.from_parts(n, violation_set.row_to_cluster, violation_set.cluster_indices)
        self.block_pairs = [BlockPair.from_conflict(conflict, self.cluster_map) for conflict in violation_set.violations]
        self.degrees = np.zeros(n, dtype=int)

        num_clusters = len(self.cluster_map.members)
        self.cluster_to_blocks: list[list[BlockMembership]] = [[] for _ in range(num_clusters)]

        self._build()

    @property
    def graph(self) -> Graph:
        return Graph(
            n=self.n,
            degrees=self.degrees,
            active=self.degrees > 0,
            deleted=np.zeros(self.n, dtype=bool),
            block_pairs=self.block_pairs,
            cluster_to_blocks=self.cluster_to_blocks,
            row_to_cluster=self.cluster_map.row_to_cluster,
        )

    def _build(self) -> None:
        for block_idx, block_pair in enumerate(self.block_pairs):
            self._add_block_pair(block_idx, block_pair)

    def _add_block_pair(self, block_idx: int, block_pair: BlockPair) -> None:
        left, right = set(block_pair.left_clusters), set(block_pair.right_clusters)
        for cid in left | right:
            self._handle_cluster(block_idx, block_pair, cid, left, right)

    def _handle_cluster(self, block_idx: int, block_pair: BlockPair, cid: int, left_cids: set, right_cids: set) -> None:
        rows = self.cluster_map.members[cid]
        in_left = cid in left_cids
        in_right = cid in right_cids

        if in_left and in_right:
            self.degrees[rows] += len(block_pair.union_members) - 1
            side = BlockSide.CLIQUE if block_pair.is_clique else BlockSide.BOTH
            self.cluster_to_blocks[cid].append(BlockMembership(block_idx, side))

        elif in_left:
            self.degrees[rows] += len(block_pair.right_members)
            self.cluster_to_blocks[cid].append(BlockMembership(block_idx, BlockSide.LEFT))

        else:
            self.degrees[rows] += len(block_pair.left_members)
            self.cluster_to_blocks[cid].append(BlockMembership(block_idx, BlockSide.RIGHT))
