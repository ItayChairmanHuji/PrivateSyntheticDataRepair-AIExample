from pathlib import Path
import pandas as pd
from s01_loading.src.loaders.loader import Loader

class DataLoader(Loader):
    def load(self, path: str | Path) -> pd.DataFrame:
        return pd.read_csv(path)
