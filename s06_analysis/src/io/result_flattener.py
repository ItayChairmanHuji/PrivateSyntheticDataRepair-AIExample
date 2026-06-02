import pandas as pd
import json
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ResultFlattener:
    """Flattens nested experiment result columns into a clean, analysis-ready format."""

    def flatten(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Main entry point for flattening. Returns (main_df, topology_df)."""
        logger.info(f"Flattening {len(df)} results...")
        
        # 1. Parse JSON columns once
        json_cols = [
            'deletion_ratio', 'runtimes', 'marginals_error', 'tvd_2way', 
            'violations', 'ml_accuracy', 'loss_function', 'metadata'
        ]
        
        parsed_data = []
        history = []
        
        for i, (_, row) in enumerate(df.iterrows()):
            if i % 100 == 0:
                logger.info(f"Processing row {i}/{len(df)}...")
            
            row_data = row.to_dict()
            
            # Parse all JSON columns for this row
            for col in json_cols:
                if col in row_data:
                    row_data[col] = self._safe_parse(row_data[col])
            
            # Extract Metrics
            row_data['deletion_ratio_val'] = row_data.get('deletion_ratio', {}).get('ratio', 0) if isinstance(row_data.get('deletion_ratio'), dict) else float(row_data.get('deletion_ratio') or 0)
            row_data['repair_runtime'] = row_data.get('runtimes', {}).get('repair', 0)
            
            merr = row_data.get('marginals_error', {})
            row_data['marginals_error_repaired'] = merr.get('repaired_avg', 0)
            row_data['marginals_error_synthetic'] = merr.get('synthetic_avg', 0)
            
            tvd = row_data.get('tvd_2way', {})
            row_data['tvd_repaired'] = tvd.get('repaired_avg', 0)
            row_data['tvd_synthetic'] = tvd.get('synthetic_avg', 0)
            
            viols = row_data.get('violations', {})
            row_data['violations_repaired'] = viols.get('repaired', 0)
            row_data['violations_synthetic'] = viols.get('synthetic', 0)
            
            ml_acc = row_data.get('ml_accuracy', {})
            rep_ml = ml_acc.get('repaired', {})
            syn_ml = ml_acc.get('synthetic', {})
            
            row_data['ml_acc_repaired'] = np.mean([v for v in rep_ml.values() if v is not None]) if rep_ml else 0
            row_data['ml_acc_synthetic'] = np.mean([v for v in syn_ml.values() if v is not None]) if syn_ml else 0
            
            for model in ['logistic_regression', 'random_forest', 'mlp']:
                row_data[f'ml_acc_{model}_repaired'] = rep_ml.get(model, 0)
                row_data[f'ml_acc_{model}_synthetic'] = syn_ml.get(model, 0)
                
            loss = row_data.get('loss_function', {})
            row_data['loss_marginal_repaired'] = loss.get('repaired', {}).get('marginal_component', 0)
            row_data['loss_marginal_synthetic'] = loss.get('synthetic', {}).get('marginal_component', 0)
            
            # Extract Topology
            meta = row_data.get('metadata', {})
            stats = meta.get('iteration_stats', [])
            
            if stats:
                alphas = [s.get('alpha') for s in stats if s.get('alpha') is not None]
                hubs = [s.get('hubbiness') for s in stats if s.get('hubbiness') is not None]
                conns = [s.get('connectivity') for s in stats if s.get('connectivity') is not None]
                
                row_data['mean_alpha'] = np.mean(alphas) if alphas else None
                row_data['mean_hubbiness'] = np.mean(hubs) if hubs else None
                row_data['mean_connectivity'] = np.mean(conns) if conns else None
                
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
            else:
                row_data['mean_alpha'] = None
                row_data['mean_hubbiness'] = None
                row_data['mean_connectivity'] = None

            parsed_data.append(row_data)

        # Create final dataframes
        df_flat = pd.DataFrame(parsed_data)
        df_topology = pd.DataFrame(history)
        
        # Rename deletion_ratio_val back to deletion_ratio if needed, or just use it
        df_flat['deletion_ratio'] = df_flat['deletion_ratio_val']

        # Final Cleanup: Force numeric
        numeric_cols = [
            'deletion_ratio', 'repair_runtime', 'ml_acc_repaired', 'ml_acc_synthetic',
            'marginals_error_repaired', 'marginals_error_synthetic',
            'tvd_repaired', 'tvd_synthetic', 'violations_repaired', 'violations_synthetic',
            'mean_alpha', 'mean_hubbiness', 'mean_connectivity', 'epsilon',
            'loss_marginal_repaired', 'loss_marginal_synthetic',
            'ml_acc_logistic_regression_repaired', 'ml_acc_random_forest_repaired', 'ml_acc_mlp_repaired'
        ]
        for col in numeric_cols:
            if col in df_flat.columns:
                df_flat[col] = pd.to_numeric(df_flat[col], errors='coerce')
                
        return df_flat, df_topology

    def _safe_parse(self, val):
        if pd.isna(val): return {}
        if isinstance(val, dict): return val
        if not isinstance(val, str): return {}
        
        val = val.strip()
        if not (val.startswith('{') or val.startswith('[')):
            return {}
            
        try:
            # Try JSON first (faster)
            return json.loads(val.replace("'", '"'))
        except:
            try:
                # Fallback to literal_eval if it's true Python dict string
                import ast
                return ast.literal_eval(val)
            except:
                return {}

