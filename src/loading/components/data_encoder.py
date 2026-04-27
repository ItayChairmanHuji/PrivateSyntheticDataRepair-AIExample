import pandas as pd
from sklearn.preprocessing import LabelEncoder

class DataEncoder:
    """Encodes categorical data to numeric values using LabelEncoder."""
    
    def __init__(self):
        self.mappings = {}

    def encode(self, data: pd.DataFrame) -> pd.DataFrame:
        encoded_data = data.copy()
        for col in encoded_data.columns:
            if not pd.api.types.is_numeric_dtype(encoded_data[col]):
                le = LabelEncoder()
                encoded_data[col] = le.fit_transform(encoded_data[col].astype(str))
                self.mappings[col] = le
        return encoded_data

    def get_mappings(self):
        return self.mappings
