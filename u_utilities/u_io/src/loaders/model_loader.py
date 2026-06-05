import dill
from pathlib import Path
from typing import Any
from .base import Loader

class ModelLoader(Loader):
    def load(self, path: Path) -> Any:
        with open(path, "rb") as f:
            return dill.load(f)

    def save(self, model: Any, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            dill.dump(model, f)
