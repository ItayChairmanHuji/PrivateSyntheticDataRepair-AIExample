from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


@dataclass(frozen=True)
class Violation:
    left: np.ndarray
    right: np.ndarray
    symmetric: bool = False


@dataclass
class ViolationSet:
    cluster_indices: List[np.ndarray]
    row_to_cluster: Optional[np.ndarray] = None
    violations: List[Violation] = field(default_factory=list)
