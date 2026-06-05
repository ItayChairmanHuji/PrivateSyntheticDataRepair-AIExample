import numpy as np
from typing import List, Set, Union, Dict
import bisect
from u_utilities.u_shared.violations import BicliqueCollection, ExplicitBiclique, RangeBiclique, GroupBiclique

class Vertex:
    def __init__(self, index: int):
        self.index = index

class VertexSeq:
    def __init__(self, graph):
        self.graph = graph
        self._data = {"original_index": np.arange(graph.n)}

    def __getitem__(self, key):
        return self._data[key]

    def select(self, **kwargs):
        if "_degree_gt" in kwargs:
            threshold = kwargs["_degree_gt"]
            if threshold == 0:
                # Optimized for WeightedVCRepairer
                return [Vertex(i) for i in self.graph.active_nodes]
            indices = np.where(self.graph._current_degrees > threshold)[0]
            return [Vertex(i) for i in indices if i not in self.graph.deleted_vertices]
        return [Vertex(i) for i in range(self.graph.n) if i not in self.graph.deleted_vertices]

class Edge:
    def __init__(self, source: int, target: int):
        self.source = source
        self.target = target

class EdgeSeq:
    def __init__(self, graph):
        self.graph = graph

    def __getitem__(self, idx: int) -> Edge:
        current_idx = 0
        for b in self.graph.bc.bicliques:
            left_active = [n for n in b.left_nodes if n not in self.graph.deleted_vertices]
            if not left_active: continue
            right_active = [n for n in b.right_nodes if n not in self.graph.deleted_vertices]
            b_size = len(left_active) * len(right_active)
            if current_idx + b_size > idx:
                rel_idx = idx - current_idx
                i = rel_idx // len(right_active)
                j = rel_idx % len(right_active)
                return Edge(int(left_active[i]), int(right_active[j]))
            current_idx += b_size
        raise IndexError("Edge index out of range")

class SymbolicConflictGraph:
    def __init__(self, n: int, bc: BicliqueCollection):
        self.n = n
        self.bc = bc
        self.deleted_vertices: Set[int] = set()
        self.vs = VertexSeq(self)
        self.es = EdgeSeq(self)
        
        # Mappings
        self._vertex_to_explicit_bicliques = [[] for _ in range(n)]
        # group_id -> list of (biclique_idx, side)
        # Note: In Multi-Group mode, we use id(row_to_group) as part of key
        self._group_to_bicliques: Dict[tuple, List] = {} 
        self._range_bicliques = []
        self._group_active_counts = {}
        
        self._current_degrees = np.zeros(n, dtype=int)
        
        for i, b in enumerate(bc.bicliques):
            if isinstance(b, GroupBiclique):
                gid = id(b.row_to_group)
                if gid not in self._group_active_counts:
                    self._group_active_counts[gid] = np.array([len(g) for g in b.group_indices])
                
                key_l = (gid, b.g1)
                if key_l not in self._group_to_bicliques: self._group_to_bicliques[key_l] = []
                self._group_to_bicliques[key_l].append((i, 'left'))
                
                if b.g1 != b.g2:
                    key_r = (gid, b.g2)
                    if key_r not in self._group_to_bicliques: self._group_to_bicliques[key_r] = []
                    self._group_to_bicliques[key_r].append((i, 'right'))
                
                # Initial degrees
                if b.g1 == b.g2:
                    self._current_degrees[b.left_nodes] += (len(b.left_nodes) - 1)
                else:
                    self._current_degrees[b.left_nodes] += len(b.right_nodes)
                    self._current_degrees[b.right_nodes] += len(b.left_nodes)
            elif isinstance(b, RangeBiclique):
                self._range_bicliques.append(i)
                # Range left side nodes must still be mapped explicitly
                for node in b.left_nodes: self._vertex_to_explicit_bicliques[node].append((i, 'left'))
                self._current_degrees[b.left_nodes] += (b.end - b.start)
                self._current_degrees[b.all_indices[b.start:b.end]] += len(b.left_nodes)
            else:
                # ExplicitBiclique
                for node in b.left_nodes: self._vertex_to_explicit_bicliques[node].append((i, 'left'))
                for node in b.right_nodes: self._vertex_to_explicit_bicliques[node].append((i, 'right'))
                self._current_degrees[b.left_nodes] += len(b.right_nodes)
                self._current_degrees[b.right_nodes] += len(b.left_nodes)

        self.active_nodes = set(np.where(self._current_degrees > 0)[0])

    def ecount(self) -> int:
        # Sum of degrees is accurate if we handle self-loops in degree calculation
        return sum(self._current_degrees[list(self.active_nodes)]) // 2

    def degree(self, indices: Union[int, List[int], np.ndarray] = None) -> Union[int, List[int], np.ndarray]:
        if indices is None: return self._current_degrees
        return self._current_degrees[indices]

    def delete_edges(self, v_idx: int):
        if v_idx in self.deleted_vertices: return
        self.deleted_vertices.add(v_idx)
        if v_idx in self.active_nodes: self.active_nodes.remove(v_idx)
        
        # 1. Update based on Group Bicliques
        # Find all groupings this vertex belongs to
        # In our engines, we know exactly which row belongs to which group
        # But for generic SymbolicConflictGraph, we check all active groupings
        for gid, active_counts in self._group_active_counts.items():
            # Find the row_to_group mapping for this gid
            # We need to find a biclique that uses this gid to get the mapping
            # (In practice, we only have few gids)
            # Find any biclique with this gid
            b_sample = next(b for b in self.bc.bicliques if isinstance(b, GroupBiclique) and id(b.row_to_group) == gid)
            g_idx = b_sample.row_to_group[v_idx]
            active_counts[g_idx] -= 1
            
            # Find which bicliques of this group are affected
            for b_idx, side in self._group_to_bicliques.get((gid, g_idx), []):
                b = self.bc.bicliques[b_idx]
                # If v was in G1, it was a neighbor to all in G2
                other_g = b.g2 if side == 'left' else b.g1
                if b.g1 == b.g2:
                    # Clique: neighbors were all in same group
                    neighbor_indices = b.group_indices[g_idx]
                else:
                    neighbor_indices = b.group_indices[other_g]
                
                # Decrement degrees and update active set
                self._current_degrees[neighbor_indices] -= 1
                # Bulk update active nodes is faster? 
                # For now just iterate if it's small groups.
                for n in neighbor_indices:
                    if self._current_degrees[n] == 0 and n in self.active_nodes:
                        self.active_nodes.remove(n)

        # 2. Update based on Explicit/Range Bicliques
        for b_idx, side in self._vertex_to_explicit_bicliques[v_idx]:
            b = self.bc.bicliques[b_idx]
            other_side = b.right_nodes if side == 'left' else b.left_nodes
            self._current_degrees[other_side] -= 1
            for n in other_side:
                if self._current_degrees[n] == 0 and n in self.active_nodes:
                    self.active_nodes.remove(n)

        # 3. Range neighbors
        for b_idx in self._range_bicliques:
            b = self.bc.bicliques[b_idx]
            pos = bisect.bisect_left(b.all_indices, v_idx, b.start, b.end)
            if pos < b.end and b.all_indices[pos] == v_idx:
                self._current_degrees[b.left_nodes] -= 1
                for n in b.left_nodes:
                    if self._current_degrees[n] == 0 and n in self.active_nodes:
                        self.active_nodes.remove(n)

    def incident(self, v_idx: int):
        return v_idx

    def simplify(self):
        pass
