import json
from pathlib import Path
from .loader import Loader

class MetadataLoader(Loader):
    def load(self, path: str | Path) -> dict:
        path = Path(path)
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
