import numpy as np
import igraph as ig
from typing import List, Set, Union, Dict
import bisect
from shared.entities.violations import BicliqueCollection, ExplicitBiclique, RangeBiclique, GroupBiclique

class Vertex:
    def __init__(self, index: int):
        self.index = index

class VertexSeq:
    def __init__(self, graph):
        self.graph = graph

    def select(self, **kwargs):
        if "_degree_gt" in kwargs:
            threshold = kwargs["_degree_gt"]
            if threshold == 0:
                # Optimized: Return indices of all nodes with edges
                return np.where(self.graph._active_mask)[0]
            indices = np.where(self.graph._current_degrees > threshold)[0]
            return indices
        return np.where(self.graph._current_degrees >= 0)[0]

class GroupAwareGraph:
    """
    Optimized graph representation that works on value groups.
    Exposes row-level API but internally uses a group-level igraph.Graph.
    """
    def __init__(self, n_rows: int, bc: BicliqueCollection):
        self.n_rows = n_rows
        self.bc = bc
        self.row_to_group = bc.row_to_group
        self.group_indices = bc.group_indices
        self.deleted_rows = np.zeros(n_rows, dtype=bool)
        
        # 1. Build group-level graph
        n_groups = len(bc.group_indices)
        edges = []
        for b in bc.bicliques:
            if isinstance(b, GroupBiclique):
                if b.g1 == b.g2:
                    # Self-loop in group graph means internal conflicts. 
                    # We can't have real self-loops in igraph for some algorithms, 
                    # but here it just means the group must be deleted if any edge exists.
                    # We'll handle this by giving it a virtual edge or high degree.
                    pass 
                edges.append((b.g1, b.g2))
        
        self.g = ig.Graph(n_groups, edges)
        self.g.simplify() # Remove duplicate edges and self-loops
        
        # Handle internal group conflicts (cliques)
        # Groups with internal conflicts MUST be deleted.
        self.must_delete_groups = set()
        for b in bc.bicliques:
            if isinstance(b, GroupBiclique) and b.g1 == b.g2:
                self.must_delete_groups.add(b.g1)

        self.vs = VertexSeq(self)
        self._update_active_mask()

    def _update_active_mask(self):
        # A row is active if its group has degree > 0 or is in must_delete_groups
        # AND the row hasn't been deleted yet.
        group_degrees = np.array(self.g.degree())
        active_groups = (group_degrees > 0) | np.array([i in self.must_delete_groups for i in range(len(group_degrees))])
        self._active_mask = active_groups[self.row_to_group] & (~self.deleted_rows)

    def ecount(self) -> int:
        return self.g.ecount() + len(self.must_delete_groups)

    def degree(self, indices: Union[int, List[int], np.ndarray] = None) -> np.ndarray:
        # Degree of a row is the degree of its group in the group graph.
        # We also add a "bonus" degree for groups that MUST be deleted.
        group_degrees = np.array(self.g.degree())
        for g_idx in self.must_delete_groups:
            group_degrees[g_idx] += 1000000 # Force selection
            
        if indices is None:
            return group_degrees[self.row_to_group]
        return group_degrees[self.row_to_group[indices]]

    def delete_edges(self, row_idx: int):
        if self.deleted_rows[row_idx]: return
        
        g_idx = self.row_to_group[row_idx]
        
        # Delete ALL rows in this group
        rows_in_group = self.group_indices[g_idx]
        self.deleted_rows[rows_in_group] = True
        
        # Delete the group from the graph
        # In igraph, deleting a vertex changes IDs. 
        # Instead, we just remove all its edges.
        if g_idx < self.g.vcount():
            incident_edges = self.g.incident(g_idx)
            self.g.delete_edges(incident_edges)
        
        if g_idx in self.must_delete_groups:
            self.must_delete_groups.remove(g_idx)
            
        self._update_active_mask()

    def incident(self, row_idx: int):
        return row_idx

class SymbolicConflictGraph:
    def __init__(self, n: int, bc: BicliqueCollection):
        self.n = n
        self.bc = bc
        self.deleted_vertices = np.zeros(n, dtype=bool)
        self.vs = VertexSeq(self)
        
        # Mappings
        self._vertex_to_explicit_bicliques = [[] for _ in range(n)]
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
                for node in b.left_nodes: self._vertex_to_explicit_bicliques[node].append((i, 'left'))
                self._current_degrees[b.left_nodes] += (b.end - b.start)
                self._current_degrees[b.all_indices[b.start:b.end]] += len(b.left_nodes)
            else:
                for node in b.left_nodes: self._vertex_to_explicit_bicliques[node].append((i, 'left'))
                for node in b.right_nodes: self._vertex_to_explicit_bicliques[node].append((i, 'right'))
                self._current_degrees[b.left_nodes] += len(b.right_nodes)
                self._current_degrees[b.right_nodes] += len(b.left_nodes)

        self._active_mask = self._current_degrees > 0
        self._total_edges = np.sum(self._current_degrees) // 2

    def ecount(self) -> int:
        return self._total_edges

    def degree(self, indices: Union[int, List[int], np.ndarray] = None) -> Union[int, List[int], np.ndarray]:
        if indices is None: return self._current_degrees
        return self._current_degrees[indices]

    def delete_edges(self, v_idx: int):
        if self.deleted_vertices[v_idx]: return
        self.deleted_vertices[v_idx] = True
        
        v_degree = self._current_degrees[v_idx]
        if v_degree == 0: return
        
        self._total_edges -= v_degree
        self._current_degrees[v_idx] = 0
        self._active_mask[v_idx] = False
        
        # 1. Update based on Group Bicliques
        for gid, active_counts in self._group_active_counts.items():
            b_sample = next(b for b in self.bc.bicliques if isinstance(b, GroupBiclique) and id(b.row_to_group) == gid)
            g_idx = b_sample.row_to_group[v_idx]
            active_counts[g_idx] -= 1
            
            for b_idx, side in self._group_to_bicliques.get((gid, g_idx), []):
                b = self.bc.bicliques[b_idx]
                other_g = b.g2 if side == 'left' else b.g1
                neighbor_indices = b.group_indices[other_g] if b.g1 != b.g2 else b.group_indices[g_idx]
                
                # Vectorized Update
                self._current_degrees[neighbor_indices] -= 1
                # Bulk update active mask
                new_inactive = neighbor_indices[self._current_degrees[neighbor_indices] == 0]
                self._active_mask[new_inactive] = False

        # 2. Update based on Explicit/Range Bicliques
        for b_idx, side in self._vertex_to_explicit_bicliques[v_idx]:
            b = self.bc.bicliques[b_idx]
            other_side = b.right_nodes if side == 'left' else b.left_nodes
            self._current_degrees[other_side] -= 1
            new_inactive = other_side[self._current_degrees[other_side] == 0]
            self._active_mask[new_inactive] = False

        # 3. Range neighbors
        for b_idx in self._range_bicliques:
            b = self.bc.bicliques[b_idx]
            pos = bisect.bisect_left(b.all_indices, v_idx, b.start, b.end)
            if pos < b.end and b.all_indices[pos] == v_idx:
                self._current_degrees[b.left_nodes] -= 1
                new_inactive = b.left_nodes[self._current_degrees[b.left_nodes] == 0]
                self._active_mask[new_inactive] = False

    def incident(self, v_idx: int):
        return v_idx


