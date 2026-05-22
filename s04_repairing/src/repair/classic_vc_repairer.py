from dataclasses import dataclass
import random
import igraph as ig
from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s04_repairing.src.repair.vertex_cover_repairer import VertexCoverRepairer

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
