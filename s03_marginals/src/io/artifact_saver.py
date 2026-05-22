import json
from pathlib import Path
from dataclasses import dataclass
from shared.entities.marginal import MarginalSet

@dataclass
class ArtifactSaver:
    def save(self, marginals: MarginalSet, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "marginals.json", "w") as f:
            json.dump(marginals.to_dict(), f, indent=4)
