from abc import ABC, abstractmethod
from src.entities.pipeline_result import PipelineResult

class Evaluator(ABC):
    """
    Abstract base class for all evaluators.
    """
    @abstractmethod
    def evaluate(self, result: PipelineResult) -> dict:
        """
        Evaluates a PipelineResult and returns a dictionary of metrics.
        """
        pass
