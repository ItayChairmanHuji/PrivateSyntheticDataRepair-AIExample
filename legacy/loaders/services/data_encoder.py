import pandas as pd
from pandas import DataFrame
from pandas.api.types import is_object_dtype, is_string_dtype
from sklearn.preprocessing import LabelEncoder


def _should_encode(data: DataFrame, col: str) -> bool:
    return is_object_dtype(data[col]) or is_string_dtype(data[col])

def encode(data: pd.DataFrame):
    mapping = {}

    for col in data.columns:
        if not _should_encode(data, col):
            continue
        encoder = LabelEncoder()
        data[col] = encoder.fit_transform(data[col].astype(str))
        mapping[col] = {value: idx for idx, value in enumerate(encoder.classes_)}
    return data, mapping
