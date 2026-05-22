import json
from pathlib import Path
from shared.entities.marginal import MarginalSet
from s01_loading.src.loaders.loader import Loader

class MarginalsLoader(Loader):
    """
    Loader for MarginalSet objects from JSON files.
    """
    def load(self, path: Path) -> MarginalSet:
        with open(path, "r") as f:
            return MarginalSet.from_dict(json.load(f))
