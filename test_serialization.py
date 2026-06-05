import json
import numpy as np
from shared.utils.serialization_helper import NpEncoder
import os
from pathlib import Path

def test_np_serialization():
    # Test data with various NumPy types
    data = {
        "int64": np.int64(10),
        "float64": np.float64(3.14),
        "ndarray": np.array([1, 2, 3]),
        "bool_": np.bool_(True),
        "nested": {
            "list": [np.int64(1), np.float64(2.2)],
            "mixed": {"a": np.int64(5)}
        }
    }
    
    test_file = "test_metadata.json"
    try:
        # This should no longer raise TypeError
        with open(test_file, "w") as f:
            json.dump(data, f, cls=NpEncoder, indent=4)
        
        # Verify the content is valid JSON and types are converted
        with open(test_file, "r") as f:
            loaded = json.load(f)
            
        assert loaded["int64"] == 10
        assert isinstance(loaded["int64"], int)
        assert loaded["float64"] == 3.14
        assert isinstance(loaded["float64"], float)
        assert loaded["ndarray"] == [1, 2, 3]
        assert loaded["bool_"] is True
        assert loaded["nested"]["list"] == [1, 2.2]
        assert loaded["nested"]["mixed"]["a"] == 5
        
        print("Serialization test passed!")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_np_serialization()
