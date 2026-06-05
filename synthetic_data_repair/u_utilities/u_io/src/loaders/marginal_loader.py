import json
from pathlib import Path
from u_utilities.u_shared import MarginalSet
from .base import Loader

class MarginalLoader(Loader):
    def load(self, path: Path) -> MarginalSet:
        with open(path, "r") as f:
            return MarginalSet.from_dict(json.load(f))

    def save(self, marginals: MarginalSet, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(marginals.to_dict(), f, indent=4)
