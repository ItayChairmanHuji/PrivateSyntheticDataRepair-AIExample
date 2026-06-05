from pathlib import Path
from typing import Any, Dict, Optional
from u_utilities.u_shared import Dataset, MarginalSet
from .loaders import DataLoader, MarginalLoader, ModelLoader, ResultLoader
from .path_resolver import PathResolver
from .enums import DataMode

class ResourceManager:
    """
    The Facade: Orchestrates path resolution and I/O operations for the RPM framework.
    
    This class serves as the primary entry point for all file operations in the r_resources
    hierarchy. It delegates path resolution to PathResolver and actual loading/saving 
    to specialized Loader classes.
    """
    def __init__(
        self, 
        resolver: Optional[PathResolver] = None,
        data_loader: Optional[DataLoader] = None,
        model_loader: Optional[ModelLoader] = None,
        marginal_loader: Optional[MarginalLoader] = None,
        result_loader: Optional[ResultLoader] = None
    ):
        """
        Initializes the ResourceManager with optional custom components (Dependency Injection).
        """
        self.resolver = resolver or PathResolver()
        self.data = data_loader or DataLoader()
        self.models = model_loader or ModelLoader()
        self.marginals = marginal_loader or MarginalLoader()
        self.results = result_loader or ResultLoader()

    def load_dataset(self, name: str, mode: DataMode = DataMode.PRIVATE, **kwargs) -> Dataset:
        """
        Loads a Dataset (Private, Synthetic, or Repaired).
        Uses PathResolver to find the data and DataLoader to handle context discovery.
        """
        path = self.resolver.resolve("data", name=name, mode=mode, **kwargs)
        return self.data.load(path)

    def save_dataset(self, dataset: Dataset, dir_path: Path):
        """Saves a Dataset object to the specified directory."""
        self.data.save(dataset, dir_path)

    def load_model(self, path: Optional[Path] = None, **kwargs) -> Any:
        """Loads a model. Resolves path from kwargs if not provided."""
        target_path = path or self.resolver.resolve("model", **kwargs)
        return self.models.load(target_path)

    def save_model(self, model: Any, path: Optional[Path] = None, **kwargs):
        """Saves a model. Resolves path from kwargs if not provided."""
        target_path = path or self.resolver.resolve("model", **kwargs)
        self.models.save(model, target_path)
    
    def load_marginals(self, path: Optional[Path] = None, **kwargs) -> MarginalSet:
        """Loads a MarginalSet. Resolves path from kwargs if not provided."""
        target_path = path or self.resolver.resolve("marginal", **kwargs)
        return self.marginals.load(target_path)

    def save_marginals(self, ms: MarginalSet, path: Optional[Path] = None, **kwargs):
        """Saves a MarginalSet. Resolves path from kwargs if not provided."""
        target_path = path or self.resolver.resolve("marginal", **kwargs)
        self.marginals.save(ms, target_path)

    def load_results(self, path: Optional[Path] = None, **kwargs) -> Dict[str, Any]:
        """Loads experiment results. Resolves path from kwargs if not provided."""
        target_path = path or self.resolver.resolve("result", **kwargs)
        return self.results.load(target_path)

    def save_results(self, res: Dict[str, Any], path: Optional[Path] = None, **kwargs):
        """Saves experiment results. Resolves path from kwargs if not provided."""
        target_path = path or self.resolver.resolve("result", **kwargs)
        self.results.save(res, target_path)
