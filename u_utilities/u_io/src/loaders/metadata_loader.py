import json
from pathlib import Path
from .base import Loader

class MetadataLoader(Loader):
    def load(self, path: Path) -> dict:
        if not path.exists(): return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def save(self, metadata: dict, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
