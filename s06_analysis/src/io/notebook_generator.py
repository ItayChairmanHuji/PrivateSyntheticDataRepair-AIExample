import json
import argparse
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class NotebookGenerator:
    """Converts a standard Python script (with # %% markers) into a Jupyter Notebook."""

    def generate(self, template_path: Path, output_path: Path) -> Path:
        """Reads a .py file and converts it to a .ipynb file."""
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        cells = []
        # Split by # %% to create cells
        raw_cells = content.split("# %%")
        
        for raw_cell in raw_cells:
            # Clean up leading/trailing newlines
            lines = raw_cell.strip("\n").split("\n")
            if not lines or (len(lines) == 1 and lines[0].strip() == ""):
                continue
                
            # If the block starts with a markdown-style comment block, make it a markdown cell
            if lines[0].startswith("# [MARKDOWN]"):
                cell_type = "markdown"
                # Remove the marker and the leading '# ' from markdown lines
                source = [line[2:] + "\n" if line.startswith("# ") else line + "\n" for line in lines[1:]]
            else:
                cell_type = "code"
                source = [line + "\n" for line in lines]

            cells.append({
                "cell_type": cell_type,
                "metadata": {},
                "source": source,
                **({"execution_count": None, "outputs": []} if cell_type == "code" else {})
            })
        
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
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=2)
            
        logger.info(f"Generated notebook at {output_path}")
        return output_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=str, required=True, help="Path to .py template file")
    parser.add_argument("--output", type=str, required=True, help="Path to output .ipynb file")
    args = parser.parse_args()
    
    generator = NotebookGenerator()
    generator.generate(Path(args.template), Path(args.output))
