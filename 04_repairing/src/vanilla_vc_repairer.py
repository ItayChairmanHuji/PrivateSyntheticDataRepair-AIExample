import numpy as np
import igraph as ig
from src.entities.dataset import Dataset
from src.entities.marginal import MarginalSet
from src.repairing.vertex_cover_repairer import VertexCoverRepairer

class VanillaVCRepairer(VertexCoverRepairer):
    """
    Implements Vanilla Vertex Cover repair (Max Degree).
    """
    def __init__(self, alpha: float = 0.5, **kwargs):
        super().__init__()

    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> int:
        degrees = graph.degree()
        # Max degree vertex
        return np.argmax(degrees)
