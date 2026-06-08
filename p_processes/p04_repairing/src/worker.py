from dataclasses import dataclass
from typing import Any
from .engine import RepairingEngine
from p_processes.p04_repairing.src.core.repairer import Repairer

@dataclass
class RepairingWorker:
    engine: RepairingEngine
    repairer: Repairer
    dataset_name: str
    synthesizer_name: str
    repairer_name: str
    epsilon: float
    seed: int
    size: int
    noise_level: Any
    alpha: float

    def run(self):
        synthetic = self.engine.load_synthetic_dataset(
            self.dataset_name, self.synthesizer_name, self.epsilon, self.seed, self.size
        )
        marginals = self.engine.load_marginal_set(self.dataset_name, self.noise_level)
        repaired = self.repairer.repair(synthetic, marginals)
        self._save_and_log(repaired)

    def _save_and_log(self, repaired):
        path = self.engine.save_repaired_dataset(
            repaired, self.repairer_name, self.synthesizer_name, 
            self.epsilon, self.seed, self.size, self.alpha
        )
        print(f"Success [{self.repairer_name}]: Repaired data saved -> {path}")
