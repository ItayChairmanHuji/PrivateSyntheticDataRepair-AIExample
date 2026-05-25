import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class NotebookGenerator:
    """Generates an analysis notebook from a template structure."""

    def generate(self, experiment_name: str, input_path: Path, topology_path: Path, output_dir: Path) -> Path:
        """Creates a .ipynb file with pre-filled analysis cells."""
        notebook_path = output_dir / f"{experiment_name}_analysis.ipynb"
        
        cells = [
            self._markdown_cell(f"# {experiment_name.replace('_', ' ').capitalize()} Analysis"),
            self._code_cell([
                "%load_ext autoreload",
                "%autoreload 2",
                "import pandas as pd",
                "import matplotlib.pyplot as plt",
                "import seaborn as sns",
                "from pathlib import Path",
                "import sys",
                "import os",
                "",
                "# Add PROJECT ROOT to path for unambiguous modular imports",
                f"sys.path.append(r'{input_path.parent.parent.parent.absolute()}')",
                "from s06_analysis.src.analysis.plotter import AnalysisPlotter",
                "",
                f"SUMMARY_CSV = r'{input_path.absolute()}'",
                f"TOPOLOGY_CSV = r'{topology_path.absolute()}'",
                "OUTPUT_DIR = Path('plots')",
                "df = pd.read_csv(SUMMARY_CSV)",
                "df_topo = pd.read_csv(TOPOLOGY_CSV)",
                "plotter = AnalysisPlotter(output_dir=OUTPUT_DIR)",
                "print(f'Loaded {len(df)} results and {len(df_topo)} topology rows.')"
            ]),
            self._markdown_cell("## Data Preview"),
            self._code_cell(["df.head()"]),
            self._markdown_cell("## Repair Performance Trends (By Dataset)"),
            self._code_cell(["plotter.plot_repair_trends(df)"]),
            self._markdown_cell("## ML Utility vs Marginals Error (By Dataset)"),
            self._code_cell(["plotter.plot_utility_error_tradeoff(df)"]),
            self._markdown_cell("## Detailed ML Utility (By Algorithm)"),
            self._code_cell(["plotter.plot_detailed_ml_accuracy(df)"]),
            self._markdown_cell("## Data Quality Trends (Marginals Error & TVD)"),
            self._code_cell(["plotter.plot_quality_trends(df)"]),
            self._markdown_cell("## Adaptive Alpha Metrics (Epsilon Evolution)"),
            self._code_cell(["plotter.plot_adaptive_metrics(df)"]),
            self._markdown_cell("## Graph Evolution (Iteration Evolution)"),
            self._code_cell(["plotter.plot_iteration_topology(df_topo)"]),
            self._markdown_cell("## Computational Efficiency"),
            self._code_cell(["plotter.plot_runtime(df)"]),
            self._markdown_cell("## Summary Statistics"),
            self._code_cell(["plotter.generate_summary_table(df)"])
        ]
        
        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(notebook_path, "w") as f:
            json.dump(notebook, f, indent=2)
            
        return notebook_path

    def _markdown_cell(self, source: str):
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": [source + "\n"]
        }

    def _code_cell(self, source_lines: list):
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in source_lines]
        }
