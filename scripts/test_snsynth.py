import sys
import pandas as pd
import numpy as np

# Monkey patch mbi BEFORE anything else
try:
    import mbi
    from mbi.domain import Domain
    from mbi.dataset import Dataset
    from mbi.factor import Factor
    from mbi.clique_vector import CliqueVector
    from mbi.graphical_model import GraphicalModel
    from mbi.markov_random_field import MarkovRandomField
    
    mbi.Domain = Domain
    mbi.Dataset = Dataset
    mbi.Factor = Factor
    mbi.CliqueVector = CliqueVector
    mbi.GraphicalModel = GraphicalModel
    mbi.MarkovRandomField = MarkovRandomField
    
    from mbi.inference import FactoredInference
    mbi.FactoredInference = FactoredInference
    
    sys.modules['mbi'].Domain = Domain
    sys.modules['mbi'].Dataset = Dataset
    sys.modules['mbi'].Factor = Factor
    sys.modules['mbi'].CliqueVector = CliqueVector
    sys.modules['mbi'].GraphicalModel = GraphicalModel
    sys.modules['mbi'].MarkovRandomField = MarkovRandomField
    sys.modules['mbi'].FactoredInference = FactoredInference
    
    print("Monkey patched mbi successfully")
except Exception as e:
    print(f"Failed to monkey patch mbi: {e}")

try:
    from snsynth import Synthesizer
    print("snsynth imported successfully")
except ImportError as e:
    print(f"Failed to import snsynth: {e}")

data = pd.DataFrame({
    'A': np.random.randint(0, 10, 100),
    'B': np.random.choice(['a', 'b', 'c'], 100)
})

try:
    mst = Synthesizer.create("mst", epsilon=1.0)
    print("MST created")
    mst.fit(data)
    print("MST fitted")
    sample = mst.sample(10)
    print("MST sampled")
    print(sample.head())
except Exception as e:
    print(f"MST failed: {e}")

try:
    patectgan = Synthesizer.create("patectgan", epsilon=1.0)
    print("PATECTGAN created")
    patectgan.fit(data)
    print("PATECTGAN fitted")
    sample = patectgan.sample(10)
    print("PATECTGAN sampled")
except Exception as e:
    print(f"PATECTGAN failed: {e}")

try:
    aim = Synthesizer.create("aim", epsilon=1.0)
    print("AIM created")
    aim.fit(data)
    print("AIM fitted")
    sample = aim.sample(10)
    print("AIM sampled")
except Exception as e:
    print(f"AIM failed: {e}")
