import pandas as pd
from pathlib import Path

class DataLoader:
    """
    Handles loading raw CSV data into a Pandas DataFrame.
    """
    def load(self, path: str | Path) -> pd.DataFrame:
        return pd.read_csv(path)
