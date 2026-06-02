import json
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ResultAggregator:
    """Aggregates raw JSON evaluation outputs into a single flattened CSV."""
    
    def __init__(self, source_dir: Path, output_file: Path):
        self.source_dir = source_dir
        self.output_file = output_file
        
    def aggregate(self):
        """Finds all evaluation JSONs and combines them into one CSV."""
        logger.info(f"Scanning for JSON results in {self.source_dir}")
        all_records = []
        
        # Look for JSON files in the source directory (recursively)
        json_files = list(self.source_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files.")
        
        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # We expect data to be a dictionary representing a row
                # If it's a list, we add all elements
                if isinstance(data, list):
                    all_records.extend(data)
                elif isinstance(data, dict):
                    # add file path context
                    data["source_file"] = str(file_path.name)
                    all_records.append(data)
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                
        if not all_records:
            logger.warning("No records aggregated!")
            return None
            
        df = pd.DataFrame(all_records)
        
        # Serialize nested dicts/lists to strings for CSV compatibility
        # (The flattener stage handles literal_eval)
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
                df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
                
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.output_file, index=False)
        logger.info(f"Aggregated {len(df)} records to {self.output_file}")
        return df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True, help="Directory containing JSON results")
    parser.add_argument("--output", type=str, required=True, help="Output CSV file path")
    args = parser.parse_args()
    
    aggregator = ResultAggregator(Path(args.source), Path(args.output))
    aggregator.aggregate()
