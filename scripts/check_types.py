import pandas as pd
from pathlib import Path

for name in ["adult", "tax", "census", "compas"]:
    data_file = Path(f"data/{name}/data.csv")
    if data_file.exists():
        df = pd.read_csv(data_file)
        print(f"--- {name} ---")
        print(df.dtypes)
        print(df.head(1))
