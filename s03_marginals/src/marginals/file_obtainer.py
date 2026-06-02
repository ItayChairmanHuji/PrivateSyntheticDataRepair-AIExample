import json
from pathlib import Path
from dataclasses import dataclass
from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s03_marginals.src.marginals.obtainer import Obtainer

@dataclass
class FileObtainer(Obtainer):
    """
    Obtainer that loads marginals from a pre-existing file.
    """
    path: str

    def obtain(self, private_dataset: Dataset, synthetic_dataset: Dataset) -> MarginalSet:
        with open(self.path, "r") as f:
            m_set = MarginalSet.from_dict(json.load(f))
            
        if private_dataset.mappings:
            encoded_marginals = []
            for m in m_set.marginals:
                encoded_values = []
                for attr, val in zip(m.attrs, m.values):
                    mapping = private_dataset.mappings.get(attr)
                    if mapping and val in mapping:
                        encoded_values.append(mapping[val])
                    else:
                        encoded_values.append(val)
                
                from shared.entities.marginal import Marginal
                encoded_marginals.append(Marginal(
                    attrs=m.attrs,
                    values=tuple(encoded_values),
                    target=m.target
                ))
            return MarginalSet(marginals=encoded_marginals)
            
        return m_set
