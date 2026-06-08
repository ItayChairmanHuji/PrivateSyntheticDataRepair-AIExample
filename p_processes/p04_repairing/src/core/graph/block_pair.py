from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np

from u_utilities.u_shared import Violation

from .cluster_map import ClusterMap


class BlockSide(Enum):
    CLIQUE = "clique"
    LEFT = "left"
    RIGHT = "right"
    BOTH = "both"


@dataclass(frozen=True)
class BlockMembership:
    block_pair_idx: int
    side: BlockSide

    def affected_members(self, block_pair: BlockPair) -> np.ndarray:
        match self.side:
            case BlockSide.CLIQUE | BlockSide.BOTH:
                return block_pair.union_members
            case BlockSide.RIGHT:
                return block_pair.left_members
            case BlockSide.LEFT:
                return block_pair.right_members


@dataclass(frozen=True)
class BlockPair:
    left_clusters: np.ndarray
    right_clusters: np.ndarray
    # Pre-calculated member arrays for both sides
    left_members: np.ndarray
    right_members: np.ndarray
    union_members: np.ndarray  # Added for BOTH/CLIQUE cases
    is_clique: bool = False

    @classmethod
    def from_conflict(cls, conflict: Violation, clusters: ClusterMap) -> BlockPair:
        left_members = clusters.members_for(conflict.left)
        right_members = clusters.members_for(conflict.right) if not conflict.symmetric else left_members

        # Pre-calculate union once for BOTH/CLIQUE cases
        if conflict.symmetric:
            union_members = left_members
        else:
            # We use unique to avoid double counting rows that are in both sides
            union_members = np.unique(np.concatenate([left_members, right_members]))

        return cls(
            left_clusters=conflict.left,
            right_clusters=conflict.right,
            left_members=left_members,
            right_members=right_members,
            union_members=union_members,
            is_clique=conflict.symmetric,
        )
