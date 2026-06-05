import json
from pathlib import Path
from typing import Any, Dict
from .base import Loader

class ResultLoader(Loader):
    def load(self, path: Path) -> Dict[str, Any]:
        with open(path, "r") as f:
            return json.load(f)

    def save(self, results: Dict[str, Any], path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(results, f, indent=4)
