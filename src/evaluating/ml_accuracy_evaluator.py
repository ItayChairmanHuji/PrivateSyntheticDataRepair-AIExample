import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.entities.pipeline_result import PipelineResult
from src.evaluating.evaluator import Evaluator


class MLAccuracyEvaluator(Evaluator):
    """
    Evaluates ML accuracy by training models on different dataset versions
    (private, synthetic, repaired) and testing them exclusively on the full private dataset.

    Models: Logistic Regression, Random Forest, and MLP.
    """

    def evaluate(self, result: PipelineResult) -> dict:
        target = result.private_dataset.target
        p_data = result.private_dataset.data
        s_data = result.synthetic_dataset.data
        r_data = result.repaired_dataset.data

        if not target or target not in p_data.columns:
            return {"ml_accuracy": {}}

        metrics = {
            "private_gold_standard": self._train_and_score(p_data, p_data, target),
            "synthetic": self._train_and_score(s_data, p_data, target),
            "repaired": self._train_and_score(r_data, p_data, target),
        }

        return {"ml_accuracy": metrics}

    def _train_and_score(
        self, train_df: pd.DataFrame, test_df: pd.DataFrame, target: str
    ) -> dict:
        if train_df.empty or test_df.empty:
            return {"logistic_regression": 0.0, "random_forest": 0.0, "mlp": 0.0}

        X_train, X_test = (
            train_df.drop(columns=[target]),
            test_df.drop(columns=[target]),
        )
        y_train, y_test = train_df[target], test_df[target]
        X_train, X_test = X_train.align(X_test, join="inner", axis=1, fill_value=0)
        return self._run_models(X_train, y_train, X_test, y_test)

    def _run_models(self, X_train, y_train, X_test, y_test):
        models = self._get_models()
        scores = {}
        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                scores[name] = float(accuracy_score(y_test, y_pred))
            except Exception:
                scores[name] = 0.0
        return scores

    def _get_models(self):
        return {
            "logistic_regression": make_pipeline(
                StandardScaler(), LogisticRegression(max_iter=5000, random_state=42)
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100, random_state=42, n_jobs=-1
            ),
            "mlp": make_pipeline(
                StandardScaler(),
                MLPClassifier(
                    hidden_layer_sizes=(100,), max_iter=2000, random_state=42
                ),
            ),
        }
