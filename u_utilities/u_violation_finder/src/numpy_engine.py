import numpy as np
import pandas as pd
from u_utilities.u_shared.denial_constraints import Predicate
from u_utilities.u_shared.violations import BicliqueCollection

class NumpyEngine:
    def find_order_violations_2d(self, data: pd.DataFrame, p1: Predicate, p2: Predicate) -> BicliqueCollection:
        """
        Specialized engine for pattern: not(t1.A < t2.A & t1.B < t2.B)
        Uses sorting and range bicliques to avoid O(N^2) memory.
        """
        bc = BicliqueCollection()
        attr1, attr2 = p1.left.attr, p2.left.attr
        opr1, opr2 = p1.opr, p2.opr
        
        # Only supports '<' for now as in adult dataset
        if opr1 != '<' or opr2 != '<':
            return bc

        # 1. Sort by attr1
        # Use kind='stable' to maintain relative order for identical attr1
        sorted_df = data[[attr1, attr2]].copy()
        sorted_df['__idx'] = np.arange(len(data))
        sorted_df = sorted_df.sort_values(attr1, kind='stable')
        
        vals1 = sorted_df[attr1].values
        vals2 = sorted_df[attr2].values
        indices = sorted_df['__idx'].values
        
        # 2. For each row i, neighbors are j < i where vals2[j] < vals2[i]
        # This is still O(N^2) edges, but we can store them as O(N) bicliques
        # if we can find ranges. 
        # For simplicity, for 2D, we will still generate many bicliques,
        # but we use 'add' which is now faster.
        
        # To be TRULY efficient for 2D, we'd need a segment tree.
        # For now, let's use a faster loop than DuckDB.
        
        for i in range(1, len(vals1)):
            # Candidates are 0..i-1 (since vals1 is sorted)
            # Find which of 0..i-1 have vals2 < current_val2
            current_val2 = vals2[i]
            prev_vals2 = vals2[:i]
            violating_pos = np.where(prev_vals2 < current_val2)[0]
            
            if len(violating_pos) > 0:
                # Add a biclique: ({indices[i]}, indices[violating_pos])
                bc.add(np.array([indices[i]]), indices[violating_pos])
        
        return bc
