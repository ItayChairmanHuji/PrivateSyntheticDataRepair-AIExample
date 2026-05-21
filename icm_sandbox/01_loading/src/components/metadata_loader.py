import json
from pathlib import Path

class MetadataLoader:
    """
    Loads dataset metadata from JSON files.
    """
    def load(self, path: str | Path) -> dict:
        path = Path(path)
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
