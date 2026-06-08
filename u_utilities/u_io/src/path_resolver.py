from pathlib import Path

from .enums import DataMode


class PathResolver:
    """
    The Path Resolver: Maps research parameters to physical file paths in r_resources.

    This class is the single source of truth for the folder hierarchy and naming
    conventions used in the RPM architecture.
    """

    def __init__(self, root_dir: str = "."):
        """Initializes the resolver with a specific project root directory."""
        self.root = Path(root_dir)
        self.r_data = self.root / "r_resources" / "r_data"
        self.r_models = self.root / "r_resources" / "r_models"
        self.r_marginals = self.root / "r_resources" / "r_marginals"
        self.r_results = self.root / "r_resources" / "r_results"
        self.r_analysis = self.root / "r_resources" / "r_analysis"
        self.r_compact = self.root / "r_resources" / "r_compact"

    def resolve(self, category: str, **kwargs) -> Path:
        """
        Unified entry point for path resolution.

        Args:
            category: One of ["data", "model", "marginal", "result", "analysis", "compact"].
            **kwargs: Parameters required for the specific category.
        """
        match category:
            case "data":
                return self._resolve_data_path(**kwargs)
            case "model":
                return self._resolve_model_path(**kwargs)
            case "marginal":
                return self._resolve_marginal_path(**kwargs)
            case "result":
                return self._resolve_result_path(**kwargs)
            case "analysis":
                return self._resolve_analysis_path(**kwargs)
            case "compact":
                return self._resolve_compact_path(**kwargs)
            case _:
                raise ValueError(f"Unknown path category: {category}")

    def _resolve_data_path(self, **kwargs) -> Path:
        mode = kwargs.get("mode", DataMode.PRIVATE)
        match mode:
            case DataMode.PRIVATE:
                return self._resolve_private_data_path(**kwargs)
            case DataMode.SYNTHETIC:
                return self._resolve_synthetic_data_path(**kwargs)
            case DataMode.REPAIRED:
                return self._resolve_repaired_data_path(**kwargs)
            case _:
                raise ValueError(f"Unknown data mode: {mode}")

    def _resolve_private_data_path(self, **kwargs) -> Path:
        """Resolves r_resources/r_data/{name}/private/data.csv"""
        return self.r_data / kwargs["name"] / "private" / "data.csv"

    def _resolve_synthetic_data_path(self, **kwargs) -> Path:
        """Resolves r_resources/r_data/{name}/synthetic/{synth}/{eps}/{seed}/{size}/data.csv"""
        return (
            self.r_data
            / kwargs["name"]
            / "synthetic"
            / kwargs["synth_name"]
            / str(kwargs["epsilon"])
            / str(kwargs["seed"])
            / str(kwargs["size"])
            / "data.csv"
        )

    def _resolve_repaired_data_path(self, **kwargs) -> Path:
        """Resolves r_resources/r_data/{name}/repaired/{repairer}/{synth}/{eps}/{seed}/{size}/{noise}/{alpha}/data.csv"""
        return (
            self.r_data
            / kwargs["name"]
            / "repaired"
            / kwargs["repairer_name"]
            / kwargs["synth_name"]
            / str(kwargs["epsilon"])
            / str(kwargs["seed"])
            / str(kwargs["size"])
            / str(kwargs["noise_level"])
            / str(kwargs["alpha"])
            / "data.csv"
        )

    def _resolve_compact_path(self, **kwargs) -> Path:
        """
        Resolves the path for a compact dataset.
        Requires: dataset_name, mode, attributes (list).
        Optional: synth_name, epsilon, seed, size, repairer_name, alpha.
        """
        base = self.r_compact / kwargs["dataset_name"] / str(kwargs["mode"])
        
        # Build identifier for source parameters
        if kwargs["mode"] == DataMode.PRIVATE:
            source_id = "default"
        elif kwargs["mode"] == DataMode.SYNTHETIC:
            source_id = f"{kwargs['synth_name']}_{kwargs['epsilon']}_{kwargs['seed']}_{kwargs['size']}"
        else: # REPAIRED
            source_id = f"{kwargs['repairer_name']}_{kwargs['synth_name']}_{kwargs['epsilon']}_{kwargs['seed']}_{kwargs['size']}_{kwargs['alpha']}"
            
        attr_id = "_".join(sorted(kwargs["attributes"]))
        return base / source_id / attr_id

    def _resolve_model_path(self, **kwargs) -> Path:
        return (
            self.r_models
            / kwargs["dataset_name"]
            / kwargs["synth_name"]
            / str(kwargs["epsilon"])
            / f"{kwargs['seed']}.pkl"
        )

    def _resolve_marginal_path(self, **kwargs) -> Path:
        return self.r_marginals / kwargs["dataset_name"] / str(kwargs["noise_level"]) / "marginals.json"

    def _resolve_result_path(self, **kwargs) -> Path:
        return self.r_results / kwargs["experiment_id"] / kwargs["timestamp"]

    def _resolve_analysis_path(self, **kwargs) -> Path:
        return self.r_analysis / kwargs["experiment_id"]

    def get_private_data_dir(self, dataset_name: str) -> Path:
        return self.resolve("data", name=dataset_name, mode=DataMode.PRIVATE)
