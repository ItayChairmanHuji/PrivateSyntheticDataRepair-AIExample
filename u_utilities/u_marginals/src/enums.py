from enum import Enum

class SelectionMethod(Enum):
    TOP_K = "top_k"
    RANDOM = "random"
    FILE = "file"

class ErrorMetric(Enum):
    L1 = "l1"
    RMSE = "rmse"
    ABS = "abs"
