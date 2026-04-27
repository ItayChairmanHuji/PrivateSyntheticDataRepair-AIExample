import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from src.evaluating.evaluator import Evaluator
from src.entities.pipeline_result import PipelineResult

class MLAccuracyEvaluator(Evaluator):
    """
    Evaluates ML accuracy of models trained on private, synthetic, and repaired data,
    all tested on a held-out portion of the private data.
    """
    def evaluate(self, result: PipelineResult) -> dict:
        target = result.private_dataset.target
        if not target or target not in result.private_dataset.data.columns:
            return {"ml_accuracy": {}}

        # 1. Split private data into train/test
        p_train, p_test = train_test_split(result.private_dataset.data, test_size=0.2, random_state=42)
        
        y_test = p_test[target]
        X_test = p_test.drop(columns=[target])

        # Helper to train and evaluate
        def get_accs(train_df):
            if train_df.empty: return {"random_forest": 0.0, "logistic_regression": 0.0}
            X_train = train_df.drop(columns=[target])
            y_train = train_df[target]
            
            # RF
            rf = RandomForestClassifier(n_estimators=100, random_state=42)
            rf.fit(X_train, y_train)
            y_pred_rf = rf.predict(X_test)
            
            # LR
            lr = LogisticRegression(max_iter=1000, random_state=42)
            lr.fit(X_train, y_train)
            y_pred_lr = lr.predict(X_test)
            
            return {
                "random_forest": accuracy_score(y_test, y_pred_rf),
                "logistic_regression": accuracy_score(y_test, y_pred_lr)
            }

        accs_private = get_accs(p_train)
        accs_synthetic = get_accs(result.synthetic_dataset.data)
        accs_repaired = get_accs(result.repaired_dataset.data)

        return {
            "ml_accuracy": {
                "private_gold_standard": accs_private,
                "synthetic": accs_synthetic,
                "repaired": accs_repaired
            }
        }
