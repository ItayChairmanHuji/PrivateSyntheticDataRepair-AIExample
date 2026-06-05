from typing import List
from u_utilities.u_shared import Dataset, Marginal, MarginalSet

class MarginalEncoder:
    """Worker: Encodes marginal values based on dataset mappings."""

    def encode(self, m_set: MarginalSet, dataset: Dataset) -> MarginalSet:
        """Encodes marginal values using the dataset's categorical mappings."""
        if not dataset.mappings:
            return m_set
            
        encoded_marginals = [
            self._encode_single(m, dataset.mappings) 
            for m in m_set.marginals
        ]
        return MarginalSet(marginals=encoded_marginals)

    def _encode_single(self, m: Marginal, mappings: dict) -> Marginal:
        encoded_values = []
        for attr, val in zip(m.attrs, m.values):
            mapping = mappings.get(attr)
            if mapping and val in mapping:
                encoded_values.append(mapping[val])
            else:
                encoded_values.append(val)
        
        return Marginal(
            attrs=m.attrs,
            values=tuple(encoded_values),
            target=m.target
        )
