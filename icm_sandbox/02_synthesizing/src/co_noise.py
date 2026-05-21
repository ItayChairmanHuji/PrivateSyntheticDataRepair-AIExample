import random
import pandas as pd
import numpy as np
from dataclasses import dataclass
from src.entities.dataset import Dataset
from src.synthesizing.synthesizer import Synthesizer
from src.entities.denial_constraints import Predicate

@dataclass
class CoNoise(Synthesizer):
    """
    Implements the Co-Noise algorithm to add violations to a dataset.
    """
    num_of_iterations: int
    seed: int = 42

    def synthesize(self, dataset: Dataset) -> Dataset:
        # Set seeds for reproducibility
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # Work on a copy of the data to avoid modifying the original
        synthetic_data = dataset.data.copy()
        
        if not dataset.dcs or not dataset.dcs.constraints:
            return Dataset(
                name=f"{dataset.name}_co_noise",
                data=synthetic_data,
                dcs=dataset.dcs,
                target=dataset.target
            )

        for _ in range(self.num_of_iterations):
            self._run_iteration(synthetic_data, dataset)

        return Dataset(
            name=f"{dataset.name}_co_noise",
            data=synthetic_data,
            dcs=dataset.dcs,
            target=dataset.target
        )

    def _run_iteration(self, data: pd.DataFrame, dataset: Dataset):
        # (1) Randomly select a constraint
        dc = random.choice(dataset.dcs.constraints)
        
        # (2) Randomly select two tuples
        idx1, idx2 = random.sample(range(len(data)), 2)
        t1 = data.iloc[idx1].copy()
        t2 = data.iloc[idx2].copy()
        
        tuples = {1: t1, 2: t2}
        
        # (3) For every predicate
        for pred in dc.predicates:
            if not self._evaluate_predicate(pred, tuples):
                self._satisfy_predicate(pred, tuples, data)
        
        # Update the data with modified tuples
        data.iloc[idx1] = tuples[1]
        data.iloc[idx2] = tuples[2]

    def _evaluate_predicate(self, pred: Predicate, tuples: dict) -> bool:
        v1 = self._get_side_value(pred.left, tuples)
        v2 = self._get_side_value(pred.right, tuples)
        
        if pred.opr == "=": return v1 == v2
        if pred.opr == "!=": return v1 != v2
        if pred.opr == "<": return v1 < v2
        if pred.opr == "<=": return v1 <= v2
        if pred.opr == ">": return v1 > v2
        if pred.opr == ">=": return v1 >= v2
        return False

    def _get_side_value(self, side, tuples: dict):
        if side.is_value:
            # Assuming side.attr is already numeric if it's a value comparison 
            # or it should be converted
            try:
                return float(side.attr)
            except ValueError:
                return side.attr
        return tuples[side.index][side.attr]

    def _satisfy_predicate(self, pred: Predicate, tuples: dict, data: pd.DataFrame):
        # Choose which side to modify
        if pred.right.is_value:
            modify_idx = pred.left.index
            target_side = pred.left
            other_val = self._get_side_value(pred.right, tuples)
            opr = pred.opr
        elif pred.left.is_value:
            modify_idx = pred.right.index
            target_side = pred.right
            other_val = self._get_side_value(pred.left, tuples)
            opr = self._invert_operator(pred.opr)
        else:
            if random.random() < 0.5:
                modify_idx = pred.left.index
                target_side = pred.left
                other_val = self._get_side_value(pred.right, tuples)
                opr = pred.opr
            else:
                modify_idx = pred.right.index
                target_side = pred.right
                other_val = self._get_side_value(pred.left, tuples)
                opr = self._invert_operator(pred.opr)

        target_tuple = tuples[modify_idx]
        attr = target_side.attr
        
        # Get active domain for the attribute
        active_domain = data[attr].unique()

        if opr in ["=", "<=", ">="]:
            # For these, we can just set it to the other value to satisfy
            target_tuple[attr] = other_val
        elif opr in ["<", ">", "!="]:
            # Try to find a value in active domain that satisfies
            satisfied_values = []
            for val in active_domain:
                if self._check_condition(val, opr, other_val):
                    satisfied_values.append(val)
            
            if satisfied_values:
                target_tuple[attr] = random.choice(satisfied_values)
            else:
                # Fallback to random value in range if numeric
                if isinstance(other_val, (int, float, np.integer, np.floating)):
                    if opr == "<": target_tuple[attr] = other_val - 1
                    elif opr == ">": target_tuple[attr] = other_val + 1
                    elif opr == "!=": target_tuple[attr] = other_val + 1
                else:
                    # For categorical, just append something
                    target_tuple[attr] = f"{other_val}_noise"

    def _check_condition(self, v1, opr, v2) -> bool:
        try:
            if opr == "<": return v1 < v2
            if opr == ">": return v1 > v2
            if opr == "!=": return v1 != v2
        except:
            return False
        return False

    def _invert_operator(self, opr: str) -> str:
        return {
            "=": "=",
            "!=": "!=",
            "<": ">",
            "<=": ">=",
            ">": "<",
            ">=": "<="
        }[opr]
