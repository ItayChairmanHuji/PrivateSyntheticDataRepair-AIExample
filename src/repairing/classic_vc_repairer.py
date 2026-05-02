import random
import igraph as ig
from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet
from src.repairing.vertex_cover_repairer import VertexCoverRepairer

class ClassicVCRepairer(VertexCoverRepairer):
    """
    Implements Classic Vertex Cover repair (Random edge selection).
    """
    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> list[int]:
        # Select a random edge from the graph
        edge_idx = random.randrange(graph.ecount())
        edge = graph.es[edge_idx]
        return [edge.source, edge.target]
