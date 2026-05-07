import pandas as pd
from pathlib import Path
import os

data_dir = Path("data")
for dataset_dir in data_dir.iterdir():
    if dataset_dir.is_dir():
        data_file = dataset_dir / "data.csv"
        if data_file.exists():
            df = pd.read_csv(data_file)
            nan_count = df.isna().sum().sum()
            print(f"Dataset {dataset_dir.name}: {nan_count} NaNs, Shape: {df.shape}")
            if nan_count > 0:
                print(f"Columns with NaNs: {df.columns[df.isna().any()].tolist()}")
