import itertools
import numpy as np
import pandas as pd
from s05_evaluating.src.components.evaluator import Evaluator
from u_utilities.u_shared.pipeline_result import PipelineResult

class MarginalSelectionEvaluator(Evaluator):
    """
    Evaluates the selection quality of the obtained marginals.
    Measures how many of the "correct" (highest true utility) marginals were selected.
    Assumes DistanceUtility (absolute difference) as the ground truth for "importance".
    """
    def evaluate(self, result: PipelineResult) -> dict:
        obtained = result.obtained_marginals
        if not obtained or len(obtained) == 0:
            return {"marginal_selection_quality": {}}
        
        k = len(obtained)
        p_data = result.private_dataset.data
        s_data = result.synthetic_dataset.data
        dc_attrs = result.private_dataset.dcs.attrs if result.private_dataset.dcs else set()
        
        # Determine the "correct" (top-k) marginals based on true distance
        columns = [c for c in p_data.columns if c not in dc_attrs]
        candidates = []
        
        for attr1, attr2 in itertools.combinations(columns, 2):
            p_counts = p_data[[attr1, attr2]].value_counts(normalize=True)
            s_counts = s_data[[attr1, attr2]].value_counts(normalize=True)
            
            idx = p_counts.index.union(s_counts.index)
            p_vals = p_counts.reindex(idx, fill_value=0.0).values
            s_vals = s_counts.reindex(idx, fill_value=0.0).values
            
            distances = np.abs(p_vals - s_vals)
            for i, dist in enumerate(distances):
                # Using a tuple of (attrs, values) as the unique identifier
                # idx[i] is a tuple for MultiIndex
                candidates.append((dist, (attr1, attr2), tuple(idx[i])))
            
            # Optional: prune to keep memory usage low, similar to TopKObtainer
            if len(candidates) > 10 * k:
                candidates.sort(key=lambda x: x[0], reverse=True)
                candidates = candidates[:2 * k]
        
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_k_correct = candidates[:k]
        
        # Create a set of identifying tuples for easy comparison
        # ((attr1, attr2), (val1, val2))
        correct_set = set()
        for _, attrs, values in top_k_correct:
            correct_set.add((attrs, values))
            
        obtained_set = set()
        for m in obtained:
            # Normalize obtained marginal identifiers
            obtained_set.add((tuple(m.attrs), tuple(m.values)))
            
        intersection = correct_set.intersection(obtained_set)
        selection_quality = len(intersection) / k if k > 0 else 0.0
        
        return {
            "marginal_selection_quality": {
                "precision_at_k": float(selection_quality),
                "overlap_count": len(intersection),
                "k": k
            }
        }

