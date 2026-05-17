import mbi.graphical_model
import numpy as np

def patched_synthetic_data(self, rows=None, method='round'):
    print(f"Patched method called with rows={rows}")
    return "success"

mbi.graphical_model.GraphicalModel.synthetic_data = patched_synthetic_data

from snsynth.mst import MSTSynthesizer
# We need a dummy synthesizer or load the real one
import dill
with open("models/adult_mst.pkl", "rb") as f:
    model = dill.load(f)

print("Calling model.sample(5)")
res = model.sample(5)
print(f"Result: {res}")
