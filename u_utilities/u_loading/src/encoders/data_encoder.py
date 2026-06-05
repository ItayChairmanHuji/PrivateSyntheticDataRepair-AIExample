from dataclasses import dataclass, field
from typing import Dict

import pandas as pd
from sklearn.preprocessing import LabelEncoder


@dataclass
class DataEncoder:
    mappings: Dict[str, LabelEncoder] = field(default_factory=dict)

    def encode(self, data: pd.DataFrame) -> pd.DataFrame:
        encoded_data = data.copy()
        non_numeric = encoded_data.select_dtypes(exclude=["number"]).columns
        for col in non_numeric:
            self._encode_column(encoded_data, col)
        return encoded_data

    def _encode_column(self, df: pd.DataFrame, col: str):
        le = LabelEncoder()
        # Converting to Series with explicit index to satisfy type checkers
        encoded_values = le.fit_transform(df[col].astype(str))
        df[col] = pd.Series(encoded_values, index=df.index)
        self.mappings[col] = le
