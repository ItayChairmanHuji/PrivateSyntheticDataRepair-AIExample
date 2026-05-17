from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class LossFunctionEvaluator(Evaluator):
    """
    Logs the loss function for each dataset, defined as:
    L(D) = alpha * (n - |D|) / n + (1 - alpha) * (1 / |M|) * sum |m_D - target_m|
    """
    def evaluate(self, result: PipelineResult) -> dict:
        # Try to get alpha from repairer params, default to 0.5 if not found
        metadata = result.metadata or {}
        alpha = metadata.get("repairer_params", {}).get("alpha", 0.5)
        n = len(result.private_dataset.data)
        marginals = result.obtained_marginals
        
        datasets = {
            "synthetic": result.synthetic_dataset.data,
            "repaired": result.repaired_dataset.data
        }
        
        results = {}
        for name, data in datasets.items():
            # Size change component: (n - |D|) / n
            size_loss = (n - len(data)) / n if n > 0 else 0.0
            
            # Marginal distance component: (1 / |M|) * sum |m_D - target_m|
            if not marginals or len(marginals) == 0:
                marg_loss = 0.0
            else:
                marg_distances = [m.calculate_distance(data) for m in marginals]
                marg_loss = sum(marg_distances) / len(marg_distances)
            
            total_loss = alpha * size_loss + (1 - alpha) * marg_loss
            
            results[name] = {
                "total": total_loss,
                "size_component": size_loss,
                "marginal_component": marg_loss
            }
            
        return {"loss_function": results}
