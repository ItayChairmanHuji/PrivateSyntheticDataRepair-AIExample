from dataclasses import dataclass
import numpy as np
import igraph as ig
from u_utilities.u_shared.dataset import Dataset
from u_utilities.u_shared.marginal import MarginalSet
from old.s04_repairing.src.repair.vertex_cover_repairer import VertexCoverRepairer

@dataclass
class VanillaVCRepairer(VertexCoverRepairer):
    """
    Implements Vanilla Vertex Cover repair (Max Degree).
    """
    alpha: float = 0.5

    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> int:
        degrees = graph.degree()
        # Max degree vertex
        return int(np.argmax(degrees))
