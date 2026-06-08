from dataclasses import dataclass
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
    noise_level: float
    alpha: float

    def run(self):
        synthetic_dataset = self.engine.load_synthetic_dataset(
            self.dataset_name, self.synthesizer_name, self.epsilon, self.seed, self.size
        )
        marginals = self.engine.load_marginal_set(self.dataset_name, self.noise_level)
        
        repaired_dataset = self.repairer.repair(synthetic_dataset, marginals)
        
        output_path = self.engine.save_repaired_dataset(
            repaired_dataset, self.repairer_name, self.synthesizer_name, 
            self.epsilon, self.seed, self.size, self.alpha
        )
        
        print(f"Success [{self.repairer_name}]: Repaired data saved -> {output_path}")
