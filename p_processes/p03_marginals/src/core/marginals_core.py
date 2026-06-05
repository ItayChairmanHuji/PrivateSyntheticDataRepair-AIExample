import numpy as np
from dataclasses import dataclass
from typing import Any, List, Optional
from u_utilities.u_shared import Dataset, Marginal, MarginalSet

@dataclass
class MarginalsCore:
    """Logic: Encapsulates the marginal calculation core."""
    # Optional calculator field for Hydra configuration compatibility
    calculator: Optional[Any] = None

    def calculate(self, dataset: Dataset, noise_level: float = 0.0) -> MarginalSet:
        """
        Calculates 2-way marginals involving the target attribute.
        Adds Gaussian noise if noise_level > 0.
        """
        data = dataset.data
        target = dataset.target
        columns = [c for c in data.columns if c != target]
        
        marginals_list: List[Marginal] = []
        rng = np.random.default_rng()
        
        # Calculate 2-way marginals for each attribute paired with the target
        for attr in columns:
            if len(data) == 0:
                continue
                
            # Group by the pair and calculate normalized counts
            counts = data.groupby([attr, target], observed=True).size() / len(data)
            
            for (val1, val2), freq in counts.items():
                target_freq = freq
                
                # Add noise if requested
                if noise_level > 0:
                    # Sensitivity for a frequency is 1/N
                    scale = noise_level / len(data)
                    noise = rng.normal(0, scale)
                    target_freq = np.clip(target_freq + noise, 0.0, 1.0)
                
                marginals_list.append(Marginal(
                    attrs=(attr, target),
                    values=(self._to_native(val1), self._to_native(val2)),
                    target=float(target_freq)
                ))
        
        return MarginalSet(marginals=marginals_list)

    def _to_native(self, val: Any) -> Any:
        """Converts numpy types to native Python types for JSON serialization."""
        if isinstance(val, (np.integer, np.floating)):
            return val.item()
        if isinstance(val, np.ndarray):
            return val.tolist()
        return val
