import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.entities.denial_constraints import Side, Predicate, DenialConstraint, DenialConstraints

class TestDenialConstraints(unittest.TestCase):

    def test_side_initialization(self):
        side = Side(attr="A", index=1, is_value=False)
        self.assertEqual(side.attr, "A")
        self.assertEqual(side.index, 1)
        self.assertFalse(side.is_value)

    def test_predicate_is_unary(self):
        s1 = Side("A", 1, False)
        s2 = Side("B", 1, False)
        s3 = Side("A", 2, False)
        
        p_unary = Predicate(s1, "=", s2)
        p_binary = Predicate(s1, "=", s3)
        
        self.assertTrue(p_unary.is_unary)
        self.assertFalse(p_binary.is_unary)

    def test_predicate_attrs(self):
        s1 = Side("A", 1, False)
        s2 = Side("val", 1, True)
        p = Predicate(s1, "=", s2)
        self.assertEqual(p.attrs, {"A"})

        s3 = Side("B", 2, False)
        p2 = Predicate(s1, "=", s3)
        self.assertEqual(p2.attrs, {"A", "B"})

    def test_predicate_to_string(self):
        s1 = Side("A", 1, False)
        s2 = Side("B", 2, False)
        p = Predicate(s1, "=", s2)
        self.assertEqual(p.to_string(), "t1.A = t2.B")

        s_val = Side("NYC", 1, True)
        p2 = Predicate(s1, "=", s_val)
        self.assertEqual(p2.to_string(), "t1.A = 'NYC'")

        s_num = Side(5000, 1, True)
        p3 = Predicate(s1, ">", s_num)
        self.assertEqual(p3.to_string(), "t1.A > 5000")

    def test_dc_to_string(self):
        s1 = Side("A", 1, False)
        s2 = Side("A", 2, False)
        p = Predicate(s1, "=", s2)
        dc = DenialConstraint([p])
        self.assertEqual(dc.to_string(), "not(t1.A = t2.A)")

    def test_denial_constraints_attrs(self):
        s1 = Side("A", 1, False)
        s2 = Side("B", 2, False)
        p = Predicate(s1, "=", s2)
        dc = DenialConstraint([p])
        
        s3 = Side("C", 1, False)
        p2 = Predicate(s3, ">", Side(10, 1, True))
        dc2 = DenialConstraint([p2])
        
        dcs = DenialConstraints([dc, dc2])
        self.assertEqual(dcs.attrs, {"A", "B", "C"})

if __name__ == "__main__":
    unittest.main()
