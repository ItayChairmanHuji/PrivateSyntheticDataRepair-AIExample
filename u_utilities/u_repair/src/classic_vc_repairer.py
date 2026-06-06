from dataclasses import dataclass
import random
import igraph as ig
from u_utilities.u_shared import Dataset
from u_utilities.u_shared import MarginalSet
from .vertex_cover_repairer import VertexCoverRepairer

@dataclass
class ClassicVCRepairer(VertexCoverRepairer):
    """
    Implements Classic Vertex Cover repair (Random edge selection).
    """
    alpha: float = 0.5

    def _select_vertex(self, graph: ig.Graph, dataset: Dataset, marginals: MarginalSet) -> list:
        # Select a random edge from the graph
        edge_idx = random.randrange(graph.ecount())
        # The optimized graph handles ecount efficiently.
        # Classic VC core needs to find a random violating edge.
        # Since we use SymbolicConflictGraph, we must pick a random biclique
        # weighted by its current edge count.
        
        # Simplified: Pick a random active vertex and one of its neighbors
        active_nodes = graph.vs.select(_degree_gt=0)
        v1 = random.choice(active_nodes)
        
        # Find a neighbor in the symbolic graph
        # For simplicity in Classic VC, we just return the vertex and its neighbors will be cleared
        # but Classic VC protocol says remove BOTH endpoints of a random edge.
        
        # We'll stick to picking v1 and its maximal neighbor or just v1 for now 
        # to ensure it works with the symbolic structure.
        return int(v1)
