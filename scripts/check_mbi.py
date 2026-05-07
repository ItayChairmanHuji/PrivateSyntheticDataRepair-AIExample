import mbi
import os
print(f"mbi: {mbi}")
if hasattr(mbi, '__file__'):
    print(f"mbi.__file__: {mbi.__file__}")
else:
    print("mbi has no __file__")

try:
    from mbi import Dataset, FactoredInference, LinearMeasurement
    print("Successfully imported Dataset, FactoredInference, and LinearMeasurement from mbi")
except ImportError as e:
    print(f"ImportError: {e}")
