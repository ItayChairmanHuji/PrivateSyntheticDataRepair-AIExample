import pandas as pd
from pathlib import Path
import sys
import logging

# Add root to path
root = Path(__file__).resolve().parent.parent.parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

from s06_analysis.src.io.result_flattener import ResultFlattener

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input summary CSV")
    parser.add_argument("--output", type=str, required=True, help="Output flattened CSV")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    logger.info(f"Loading {input_path}")
    df = pd.read_csv(input_path)

    flattener = ResultFlattener()
    df_flat, df_topology = flattener.flatten(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_flat.to_csv(output_path, index=False)
    logger.info(f"Saved flattened results to {output_path}")

    # Save topology if requested or just by default
    topo_path = output_path.parent / f"{output_path.stem}_topology.csv"
    df_topology.to_csv(topo_path, index=False)
    logger.info(f"Saved topology history to {topo_path}")

if __name__ == "__main__":
    main()
