from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Loader(ABC):
    @abstractmethod
    def load(self, path: str | Path) -> Any:
        pass
