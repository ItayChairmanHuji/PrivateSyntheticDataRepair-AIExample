from typing import List, Optional, Tuple
from u_utilities.u_shared import Dataset, MarginalSet
from ..engine.resolver import MarginalResolver
from ..workers.selector import TopKSelector
from ..workers.generator import MarginalGenerator
from ..workers.encoder import MarginalEncoder
from ..enums import SelectionMethod

class MarginalManager:
    """Facade: Orchestrates marginal selection, calculation, and encoding."""

    def __init__(
        self,
        resolver: Optional[MarginalResolver] = None,
        selector: Optional[TopKSelector] = None,
        generator: Optional[MarginalGenerator] = None,
        encoder: Optional[MarginalEncoder] = None
    ):
        self.resolver = resolver or MarginalResolver()
        self.selector = selector or TopKSelector()
        self.generator = generator or MarginalGenerator()
        self.encoder = encoder or MarginalEncoder()

    def obtain(
        self, 
        p_dataset: Dataset, 
        s_dataset: Dataset, 
        method: str = "top_k",
        **kwargs
    ) -> MarginalSet:
        """High-level API to obtain marginals using various methods."""
        selection_method = self.resolver.resolve_selection_method(method)
        rng = self.resolver.resolve_rng(kwargs.get("seed"))
        
        match selection_method:
            case SelectionMethod.TOP_K:
                return self._obtain_top_k(p_dataset, s_dataset, rng, **kwargs)
            case _:
                raise ValueError(f"Method {method} not implemented.")

    def _obtain_top_k(self, p_ds, s_ds, rng, **kwargs) -> MarginalSet:
        selected = self.selector.select(
            p_ds.data, s_ds.data, 
            kwargs.get("k", 10), 
            kwargs.get("selection_budget", 1.0), 
            rng, 
            target_attr=p_ds.target,
            exclude_attrs=p_ds.dcs.attrs if kwargs.get("exclude_dc") else []
        )
        m_set = self.generator.generate_noisy(
            selected, len(p_ds.data), 
            kwargs.get("generation_budget", 1.0), 
            rng
        )
        return self.encoder.encode(m_set, p_ds)
