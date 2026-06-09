import random
from dataclasses import dataclass
from u_utilities.u_shared import MarginalSet

@dataclass
class MarginalSamplingCore:
    """Logic: Samples a subset of marginals from a MarginalSet."""
    sample_size: int = 100
    seed: int = 42

    def sample(self, marginal_set: MarginalSet) -> MarginalSet:
        """Samples sample_size marginals from the set."""
        if len(marginal_set.marginals) <= self.sample_size:
            return marginal_set
        
        rng = random.Random(self.seed)
        sampled_marginals = list(marginal_set.marginals)
        rng.shuffle(sampled_marginals)
        sampled_marginals = sampled_marginals[:self.sample_size]
        return MarginalSet(marginals=sampled_marginals)
