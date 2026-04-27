import random
import igraph as ig
from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet
from src.repairing.vertex_cover_repairer import VertexCoverRepairer

class ClassicVCRepairer(VertexCoverRepairer):
    """
    Implements Classic Vertex Cover repair (Random).
    """
    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> int:
        # Select a random vertex from the graph that has at least one edge (is not isolated)
        active_vertices = [v.index for v in graph.vs if graph.degree(v.index) > 0]
        return random.choice(active_vertices)
