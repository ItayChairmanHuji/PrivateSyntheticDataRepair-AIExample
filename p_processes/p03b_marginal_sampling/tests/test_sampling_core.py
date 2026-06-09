from p_processes.p03b_marginal_sampling.src.core.sampling_core import MarginalSamplingCore
from u_utilities.u_shared import Marginal, MarginalSet


def _marginals(count):
    return MarginalSet([
        Marginal(attrs=("A",), values=(i,), target=0.1)
        for i in range(count)
    ])


def test_sampled_marginals_are_prefix_stable():
    marginal_set = _marginals(20)

    sample_5 = MarginalSamplingCore(sample_size=5, seed=42).sample(marginal_set)
    sample_10 = MarginalSamplingCore(sample_size=10, seed=42).sample(marginal_set)

    assert sample_10.marginals[:5] == sample_5.marginals
