from dataclasses import dataclass, field
from typing import List, Set, Tuple, Optional
import numpy as np
import pandas as pd

from abc import ABC, abstractmethod

class Biclique(ABC):
    @property
    @abstractmethod
    def left_nodes(self) -> np.ndarray: pass
    
    @property
    @abstractmethod
    def right_nodes(self) -> np.ndarray: pass

@dataclass
class ExplicitBiclique(Biclique):
    _left: np.ndarray
    _right: np.ndarray

    def __post_init__(self):
        if not isinstance(self._left, np.ndarray): self._left = np.array(list(self._left))
        if not isinstance(self._right, np.ndarray): self._right = np.array(list(self._right))

    @property
    def left_nodes(self) -> np.ndarray: return self._left
    @property
    def right_nodes(self) -> np.ndarray: return self._right

@dataclass
class RangeBiclique(Biclique):
    """Represents (left_indices, [start_idx, end_idx))"""
    _left: np.ndarray
    start: int
    end: int
    all_indices: np.ndarray # Reference to a global sorted array

    @property
    def left_nodes(self) -> np.ndarray: return self._left
    
    @property
    def right_nodes(self) -> np.ndarray:
        return self.all_indices[self.start:self.end]

@dataclass
class GroupBiclique(Biclique):
    g1: int
    g2: int
    group_indices: List[np.ndarray] # Local to the grouping used by this biclique
    row_to_group: np.ndarray # Mapping row_id -> group_id for this grouping

    @property
    def left_nodes(self) -> np.ndarray: return self.group_indices[self.g1]
    @property
    def right_nodes(self) -> np.ndarray: return self.group_indices[self.g2]

@dataclass
class BicliqueCollection:
    bicliques: List[Biclique] = field(default_factory=list)
    # Optional: value grouping state to share across bicliques
    row_to_group: Optional[np.ndarray] = None
    group_indices: Optional[List[np.ndarray]] = None

    def add(self, left: np.ndarray, right: np.ndarray):
        if len(left) == 0 or len(right) == 0: return
        if len(left) == 1 and len(right) == 1:
            i, j = int(left[0]), int(right[0])
            if i == j: return
            left, right = np.array([min(i, j)]), np.array([max(i, j)])
        else:
            if np.min(left) > np.min(right):
                left, right = right, left
        self.bicliques.append(ExplicitBiclique(left, right))

    def add_group_violation(self, g1: int, g2: int):
        """Adds a violation between two value groups."""
        if self.group_indices is None or self.row_to_group is None:
            raise ValueError("group_indices and row_to_group must be set to use group violations")
        self.bicliques.append(GroupBiclique(g1, g2, self.group_indices, self.row_to_group))

    def add_range(self, left: np.ndarray, start: int, end: int, all_indices: np.ndarray):
        if len(left) == 0 or start >= end: return
        self.bicliques.append(RangeBiclique(left, start, end, all_indices))

    def is_empty(self) -> bool:
        return len(self.bicliques) == 0

    def total_edges(self) -> int:
        return sum(len(b.left_nodes) * len(b.right_nodes) for b in self.bicliques)

    @property
    def empty(self) -> bool:
        return self.is_empty()

    def to_dataframe(self) -> pd.DataFrame:
        """Warning: Can OOM on large graphs. Use only for tests/small datasets."""
        import pandas as pd
        rows = []
        for b in self.bicliques:
            for i1 in b.left_nodes:
                for i2 in b.right_nodes:
                    if i1 != i2:
                        rows.append({'idx1': i1, 'idx2': i2})
        if not rows:
            return pd.DataFrame(columns=['idx1', 'idx2'])
        return pd.DataFrame(rows)

    def __len__(self) -> int:
        return self.total_edges()

    def __bool__(self) -> bool:
        return not self.is_empty()
