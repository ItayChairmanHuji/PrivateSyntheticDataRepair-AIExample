from dataclasses import dataclass

from ..engine.loading_engine import LoadingEngine
from ..workers.file_loader import FileLoader


@dataclass
class LoadingOrchestrator:
    """Facade: Orchestrates the end-to-end loading process."""

    engine: LoadingEngine
    worker: FileLoader

    def run(self):
        """Executes the loading flow: Load -> Resolve -> Save."""
        dataset = self.worker.load()
        output_dir = self.engine.resolve_output_dir(dataset.name)

        # Use the underlying manager from the engine to save
        self.engine.manager.save_dataset(dataset, output_dir)
        print(f"Success [p01_loading]: {dataset.name} -> {output_dir}")
