import os
import time
from dataclasses import dataclass
import pandas as pd
from typing import Optional
from .engine import SamplingEngine
from .core.sampling_core import SamplingCore

@dataclass
class SamplingWorker:
    """Orchestrator: Coordinates the Engine and Logic for the sampling process."""
    engine: SamplingEngine
    core: SamplingCore
    dataset_name: str
    engine_name: str
    epsilon: float
    seed: int
    size: Optional[int] = None
    model_seed: int = 42

    def run(self):
        """Executes the sampling flow: Load Model -> Sample -> Save Data."""
        # 1. Use the Engine to load the private resource (for metadata)
        dataset = self.engine.manager.load_dataset(self.dataset_name)

        # Determine actual generation size
        gen_size = self.size if self.size is not None else len(dataset.data)

        # 2. Resolve output path and guard concurrent array tasks for the same sample.
        output_path = self.engine.resolve_synthetic_data_path(
            self.dataset_name,
            self.engine_name,
            self.epsilon,
            self.seed,
            gen_size
        )
        lock_dir = output_path.parent / ".sampling.lock"
        while True:
            try:
                os.mkdir(lock_dir)
                break
            except FileExistsError:
                time.sleep(5)

        try:
            if self._has_valid_output(output_path, dataset):
                print(f"Skipping [p02b_sampling]: {output_path} already exists.")
                return

            # 3. Use the Engine to resolve model path and load it
            model_path = self.engine.resolve_model_path(
                self.dataset_name,
                self.engine_name,
                self.epsilon,
                self.model_seed
            )
            model = self.engine.manager.load_model(model_path)

            # Update core's sampler seed if possible
            if hasattr(self.core.sampler, 'seed'):
                self.core.sampler.seed = self.seed

            # 4. Use Logic to perform sampling
            synthetic_dataset = self.core.sample(model, dataset, gen_size)

            # 5. Use the Engine's manager to save
            self.engine.manager.save_dataset(synthetic_dataset, output_path.parent)
            self._marker_path(output_path).touch()

            print(f"Success [p02b_sampling]: {self.dataset_name} -> {output_path}")
        finally:
            try:
                os.rmdir(lock_dir)
            except OSError:
                pass

    def _has_valid_output(self, output_path, private_dataset) -> bool:
        marker_path = self._marker_path(output_path)
        if marker_path.exists() and output_path.exists():
            return True
        if not output_path.exists():
            return False
        try:
            existing = pd.read_csv(output_path)
            expected_columns = list(private_dataset.data.columns)
            if len(existing) == (self.size if self.size is not None else len(private_dataset.data)) and list(existing.columns) == expected_columns:
                marker_path.touch()
                return True
        except Exception as exc:
            print(f"Invalid existing sample {output_path}; regenerating. Reason: {exc}")
        output_path.unlink(missing_ok=True)
        marker_path.unlink(missing_ok=True)
        return False

    def _marker_path(self, output_path):
        return output_path.with_suffix(output_path.suffix + ".complete")
