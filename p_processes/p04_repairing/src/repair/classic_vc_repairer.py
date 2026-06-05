from dataclasses import dataclass
import random
import igraph as ig
from u_utilities.u_shared.dataset import Dataset
from u_utilities.u_shared.marginal import MarginalSet
from old.s04_repairing.src.repair.vertex_cover_repairer import VertexCoverRepairer

@dataclass
class ClassicVCRepairer(VertexCoverRepairer):
    """
    Implements Classic Vertex Cover repair (Random edge selection).
    """
    alpha: float = 0.5

    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> list:
        # Select a random edge from the graph
        edge_idx = random.randrange(graph.ecount())
        edge = graph.es[edge_idx]
        return [edge.source, edge.target]
