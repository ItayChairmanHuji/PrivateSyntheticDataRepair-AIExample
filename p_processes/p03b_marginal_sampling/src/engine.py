from dataclasses import dataclass
from u_utilities.u_io import ResourceManager

@dataclass
class MarginalSamplingEngine:
    """Engine: Handles loading and saving sampled marginals."""
    manager: ResourceManager

    def load_marginals(self, dataset_name: str, noise_level: float):
        return self.manager.load_marginals(dataset_name=dataset_name, noise_level=noise_level)

    def save_sampled_marginals(self, marginal_set, dataset_name: str, noise_level: float, sample_size: int):
        # We need to decide on a path for sampled marginals. 
        # For now, let's use a subfolder in r_marginals or a new category.
        # The PathResolver currently resolves marginal as r_marginals/{dataset}/{noise}/marginals.json
        # We can pass an extra parameter to resolve a different filename if we modify the resolver,
        # or we can use the 'noise_level' as a string like '1.0_sampled_100'.
        
        noise_str = f"{noise_level}_sampled_{sample_size}"
        self.manager.save_marginals(marginal_set, dataset_name=dataset_name, noise_level=noise_str)
