import unittest
import sys
import os
import numpy as np
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.serialization_helper import get_serializable_params

@dataclass
class DummyObj:
    name: str
    value: int
    _private: str = "secret"

class TestSerializationHelper(unittest.TestCase):

    def test_basic_dict(self):
        d = {"a": 1, "b": "test", "c": True}
        res = get_serializable_params(d)
        self.assertEqual(res, d)

    def test_numpy_serialization(self):
        d = {"arr": np.array([1, 2, 3])}
        res = get_serializable_params(d)
        self.assertEqual(res["arr"], [1, 2, 3])
        self.assertIsInstance(res["arr"], list)

    def test_object_serialization(self):
        obj = DummyObj(name="test", value=123)
        res = get_serializable_params(obj)
        self.assertEqual(res["name"], "test")
        self.assertEqual(res["value"], 123)
        self.assertNotIn("_private", res)

    def test_nested_serialization(self):
        inner = DummyObj(name="inner", value=1)
        outer = {"outer_val": 10, "nested": inner}
        res = get_serializable_params(outer)
        self.assertEqual(res["outer_val"], 10)
        self.assertEqual(res["nested"]["name"], "inner")
        
    def test_mixed_types(self):
        d = {
            "none": None,
            "int": 1,
            "float": 1.5,
            "list": [1, np.array([2])],
            "custom": DummyObj("a", 1)
        }
        res = get_serializable_params(d)
        self.assertIsNone(res["none"])
        self.assertEqual(res["float"], 1.5)
        # Note: _process_value recursively handles lists/dicts? 
        # Looking at code: _process_value handles list by returning it as is.
        # It doesn't recursively process list elements. 
        # Let's verify that behavior in test.
        self.assertEqual(res["list"][0], 1)
        # If _process_value doesn't handle list recursion, res["list"][1] will be the np.array object's string representation?
        # Actually _process_value returns str(v) as fallback.

from dataclasses import dataclass

if __name__ == "__main__":
    unittest.main()
