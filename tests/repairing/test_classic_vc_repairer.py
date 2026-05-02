import sys
import os
import pandas as pd
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.repairing.classic_vc_repairer import ClassicVCRepairer
from src.entities.dataset import Dataset
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side
from src.entities.marginal import MarginalSet

class TestClassicVCRepairer(unittest.TestCase):

    def setUp(self):
        # A small dataset where Row 0 and Row 1 violate t1.A=t2.A & t1.B!=t2.B
        self.data = pd.DataFrame({
            'A': [1, 1, 2],
            'B': [10, 20, 10]
        })
        # DC: not(t1.A=t2.A & t1.B!=t2.B)
        p1 = Predicate(Side('A', 1, False), '=', Side('A', 2, False))
        p2 = Predicate(Side('B', 1, False), '!=', Side('B', 2, False))
        self.dcs = DenialConstraints([DenialConstraint([p1, p2])])
        
        self.ds = Dataset("dummy", self.data, self.dcs, "")
        self.marginals = MarginalSet([])

    def test_classic_vc_edge_selection(self):
        """
        Classic VC now selects an edge and removes BOTH vertices.
        In this case, there is only one edge (0, 1).
        Both Row 0 and Row 1 should be removed.
        """
        repairer = ClassicVCRepairer()
        repaired_ds = repairer.repair(self.ds, self.marginals)
        
        # Conflict: (0, 1). 
        # Selection of this edge results in both 0 and 1 being removed.
        # Only Row 2 should remain.
        self.assertEqual(len(repaired_ds.data), 1)
        self.assertEqual(repaired_ds.data.iloc[0]['A'], 2)
        self.assertEqual(repaired_ds.data.iloc[0]['B'], 10)
        
        # Remaining data should have 0 violations
        self.assertEqual(len(repaired_ds.get_violations()), 0)

if __name__ == "__main__":
    unittest.main()
