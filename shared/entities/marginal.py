from dataclasses import dataclass
from typing import Any, List, Tuple

import pandas as pd


@dataclass(frozen=True)
class Marginal:
    attrs: Tuple[str, ...]
    values: Tuple[Any, ...]
    target: float

    def to_dict(self):
        return {
            "attrs": list(self.attrs),
            "values": list(self.values),
            "target": self.target
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            attrs=tuple(d["attrs"]),
            values=tuple(d["values"]),
            target=d["target"]
        )

    def get_mask(self, data: pd.DataFrame):
        if not self.attrs:
            return pd.Series(True, index=data.index)

        mask = pd.Series(True, index=data.index)
        for attr, val in zip(self.attrs, self.values):
            col = data[attr]
            if pd.api.types.is_numeric_dtype(col):
                try:
                    # Robust numeric comparison (handles 0 == 0.0, etc.)
                    target_val = float(val)
                    mask &= (col == target_val)
                except (ValueError, TypeError):
                    # If val cannot be numeric but col is, no matches possible
                    mask &= pd.Series(False, index=data.index)
            else:
                # String/Categorical comparison
                mask &= (col.astype(str) == str(val))
        return mask

    def calculate_frequency(self, data: pd.DataFrame) -> float:
        if len(data) == 0:
            return 0.0
        return len(data[self.get_mask(data)]) / len(data)

    def calculate_error(self, data: pd.DataFrame) -> float:
        freq = self.calculate_frequency(data)
        distance = abs(freq - self.target)
        # Use a small epsilon to avoid division by zero (Relative Error)
        return distance / (self.target + 1e-10)

    def calculate_distance(self, data: pd.DataFrame) -> float:
        freq = self.calculate_frequency(data)
        return abs(freq - self.target)


@dataclass
class MarginalSet:
    marginals: List[Marginal]

    def to_dict(self):
        return {"marginals": [m.to_dict() for m in self.marginals]}

    @classmethod
    def from_dict(cls, d):
        return cls(marginals=[Marginal.from_dict(m) for m in d["marginals"]])

    def __len__(self):
        return len(self.marginals)

    def __iter__(self):
        return iter(self.marginals)
