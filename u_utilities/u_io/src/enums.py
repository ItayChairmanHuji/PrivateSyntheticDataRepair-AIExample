from enum import Enum

class DataMode(Enum):
    """The 'flavor' or stage of a dataset."""
    PRIVATE = "private"
    SYNTHETIC = "synthetic"
    REPAIRED = "repaired"
