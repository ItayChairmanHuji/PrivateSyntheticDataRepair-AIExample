from dataclasses import dataclass

from .core.loading_core import LoadingCore
from .engine import LoadingEngine


@dataclass
class LoadingWorker:
    """Orchestrator: Coordinates the Engine and Logic for the loading process."""

    engine: LoadingEngine
    core: LoadingCore

    def run(self):
        """Executes the loading flow: Load -> Resolve -> Save."""

        dataset = self.core.load()
        output_dir = self.engine.resolve_output_dir(dataset.name)
        self.engine.save_dataset(dataset, output_dir)

        print(f"Success [p01_loading]: {dataset.name} -> {output_dir}")
