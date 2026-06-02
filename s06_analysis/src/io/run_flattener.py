import pandas as pd
from pathlib import Path
from s06_analysis.src.io.result_flattener import ResultFlattener
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    flattener = ResultFlattener()
    main_df, topology_df = flattener.flatten(df)

    main_df.to_csv(args.output, index=False)
    logger.info(f"Saved flattened results to {args.output}")

if __name__ == "__main__":
    main()
