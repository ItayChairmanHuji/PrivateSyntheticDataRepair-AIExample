import pandas as pd
from u_utilities.u_shared import DenialConstraints, BicliqueCollection
from u_utilities.u_violation_finder.src.value_grouped_engine import ValueGroupedEngine

class ViolationFinder:
    def __init__(self):
        self.value_grouped = ValueGroupedEngine()

    def find_violations(self, data: pd.DataFrame, dcs: DenialConstraints) -> BicliqueCollection:
        bc = BicliqueCollection()
        if len(data) == 0 or len(dcs.constraints) == 0:
            return bc

        for dc in dcs.constraints:
            try:
                res_bc = self.value_grouped.find_violations(data, dc)
                
                # Merge bicliques
                bc.bicliques.extend(res_bc.bicliques)
                
                # If the engine provided grouping state, use it
                if res_bc.row_to_group is not None:
                    bc.row_to_group = res_bc.row_to_group
                    bc.group_indices = res_bc.group_indices
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error processing DC {dc.to_string()}: {e}")

        return bc
