import random
import igraph as ig
from shared.entities.dataset import Dataset
from shared.entities.marginal import MarginalSet
from s04_repairing.src.vertex_cover_repairer import VertexCoverRepairer

class ClassicVCRepairer(VertexCoverRepairer):
    """
    Implements Classic Vertex Cover repair (Random edge selection).
    """
    def __init__(self, alpha: float = 0.5, **kwargs):
        super().__init__()

    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> list[int]:
        # Select a random edge from the graph
        edge_idx = random.randrange(graph.ecount())
        edge = graph.es[edge_idx]
        return [edge.source, edge.target]

