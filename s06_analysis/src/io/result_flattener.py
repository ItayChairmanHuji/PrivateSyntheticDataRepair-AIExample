import pandas as pd
import ast
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ResultFlattener:
    """Flattens nested experiment result columns into a clean, analysis-ready format."""

    def flatten(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Main entry point for flattening. Returns (main_df, topology_df)."""
        logger.info(f"Flattening {len(df)} results...")
        
        # 1. Basic Metric Extraction
        df['deletion_ratio'] = df.apply(self._get_deletion_ratio, axis=1)
        df['repair_runtime'] = df.apply(self._get_repair_runtime, axis=1)
        df['marginals_error_repaired'] = df.apply(self._get_marginals_error, axis=1, key='repaired_avg')
        df['marginals_error_synthetic'] = df.apply(self._get_marginals_error, axis=1, key='synthetic_avg')
        
        # 2. TVD and Violations
        df['tvd_repaired'] = df.apply(self._get_tvd, axis=1, key='repaired_avg')
        df['tvd_synthetic'] = df.apply(self._get_tvd, axis=1, key='synthetic_avg')
        df['violations_repaired'] = df.apply(self._get_violations, axis=1, key='repaired')
        df['violations_synthetic'] = df.apply(self._get_violations, axis=1, key='synthetic')

        # 3. ML Accuracy (Averaged and Specific)
        df['ml_acc_repaired'] = df.apply(self._get_ml_acc, axis=1, key='repaired')
        df['ml_acc_synthetic'] = df.apply(self._get_ml_acc, axis=1, key='synthetic')
        
        for model in ['logistic_regression', 'random_forest', 'mlp']:
            df[f'ml_acc_{model}_repaired'] = df.apply(self._get_model_acc, axis=1, key='repaired', model=model)
            df[f'ml_acc_{model}_synthetic'] = df.apply(self._get_model_acc, axis=1, key='synthetic', model=model)

        # 4. Loss Components
        df['loss_marginal_repaired'] = df.apply(self._get_loss, axis=1, key='repaired', component='marginal_component')
        df['loss_marginal_synthetic'] = df.apply(self._get_loss, axis=1, key='synthetic', component='marginal_component')
        
        # 5. Adaptive VC Metrics (Alpha, Hubbiness, Connectivity)
        topology_df = self._extract_topology_history(df)
        df = self._extract_mean_topology(df)
        
        # 6. Final Cleanup: Force numeric
        numeric_cols = [
            'deletion_ratio', 'repair_runtime', 'ml_acc_repaired', 'ml_acc_synthetic',
            'marginals_error_repaired', 'marginals_error_synthetic',
            'tvd_repaired', 'tvd_synthetic', 'violations_repaired', 'violations_synthetic',
            'mean_alpha', 'mean_hubbiness', 'mean_connectivity', 'epsilon',
            'loss_marginal_repaired', 'loss_marginal_synthetic',
            'ml_acc_logistic_regression_repaired', 'ml_acc_random_forest_repaired', 'ml_acc_mlp_repaired'
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df, topology_df

    def _safe_parse(self, val):
        if pd.isna(val): return {}
        if isinstance(val, dict): return val
        try:
            # Handle potential malformed or double-encoded strings
            if isinstance(val, str) and val.strip().startswith('{'):
                return ast.literal_eval(val)
            return {}
        except:
            return {}

    def _get_deletion_ratio(self, row):
        val = self._safe_parse(row.get('deletion_ratio'))
        return val.get('ratio', 0) if isinstance(val, dict) else float(val or 0)

    def _get_repair_runtime(self, row):
        val = self._safe_parse(row.get('runtimes'))
        return val.get('repair', 0)

    def _get_marginals_error(self, row, key='repaired_avg'):
        val = self._safe_parse(row.get('marginals_error'))
        return val.get(key, 0)

    def _get_tvd(self, row, key='repaired_avg'):
        val = self._safe_parse(row.get('tvd_2way'))
        return val.get(key, 0)

    def _get_violations(self, row, key='repaired'):
        val = self._safe_parse(row.get('violations'))
        return val.get(key, 0)

    def _get_ml_acc(self, row, key='repaired'):
        val = self._safe_parse(row.get('ml_accuracy'))
        results = val.get(key, {})
        if not results: return 0
        vals = [v for v in results.values() if v is not None]
        return np.mean(vals) if vals else 0

    def _get_model_acc(self, row, key='repaired', model='logistic_regression'):
        val = self._safe_parse(row.get('ml_accuracy'))
        return val.get(key, {}).get(model, 0)

    def _get_loss(self, row, key='repaired', component='marginal_component'):
        val = self._safe_parse(row.get('loss_function'))
        return val.get(key, {}).get(component, 0)

    def _extract_topology_history(self, df: pd.DataFrame) -> pd.DataFrame:
        """Expands iteration_stats into a long-form dataframe for history plotting."""
        history = []
        for _, row in df.iterrows():
            meta = self._safe_parse(row.get('metadata'))
            stats = meta.get('iteration_stats', [])
            for s in stats:
                history.append({
                    "dataset": row["dataset"],
                    "synthesizer": row["synthesizer"],
                    "epsilon": row["epsilon"],
                    "seed": row["seed"],
                    "repair_algorithm": row["repair_algorithm"],
                    "iteration": s.get("iteration"),
                    "alpha": s.get("alpha"),
                    "hubbiness": s.get("hubbiness"),
                    "connectivity": s.get("connectivity"),
                    "n_active": s.get("n_active"),
                    "n_edges": s.get("n_edges")
                })
        return pd.DataFrame(history)

    def _extract_mean_topology(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates mean topology stats for the summary dataframe."""
        def get_stats(row):
            meta = self._safe_parse(row.get('metadata'))
            stats = meta.get('iteration_stats', [])
            if not stats: return pd.Series([None, None, None])
            
            alphas = [s.get('alpha') for s in stats if s.get('alpha') is not None]
            hubs = [s.get('hubbiness') for s in stats if s.get('hubbiness') is not None]
            conns = [s.get('connectivity') for s in stats if s.get('connectivity') is not None]
            
            return pd.Series([
                np.mean(alphas) if alphas else None,
                np.mean(hubs) if hubs else None,
                np.mean(conns) if conns else None
            ])

        df[['mean_alpha', 'mean_hubbiness', 'mean_connectivity']] = df.apply(get_stats, axis=1)
        return df
