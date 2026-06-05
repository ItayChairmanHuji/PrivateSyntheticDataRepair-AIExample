from typing import Optional
import numpy as np
from ..enums import SelectionMethod

class MarginalResolver:
    """Engine: Resolves selection logic and parameters for marginals."""

    def resolve_rng(self, seed: Optional[int]) -> np.random.Generator:
        """Resolves the random number generator."""
        return np.random.default_rng(seed or 42)

    def resolve_selection_method(self, method: str) -> SelectionMethod:
        """Resolves selection method from string or enum."""
        if isinstance(method, SelectionMethod):
            return method
        return SelectionMethod(method.lower())
