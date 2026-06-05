from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any

class Loader(ABC):
    @abstractmethod
    def load(self, path: Path) -> Any:
        pass

    @abstractmethod
    def save(self, data: Any, path: Path) -> None:
        pass
