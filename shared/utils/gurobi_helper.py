import gurobipy as gp
import json
import os

class GurobiHelper:
    _env = None

    @classmethod
    def get_env(cls):
        if cls._env is None:
            cls._env = cls._initialize_env()
        return cls._env

    @classmethod
    def _initialize_env(cls):
        license_path = "license.json"
        if os.path.exists(license_path):
            return cls._load_env_from_license(license_path)
        return gp.Env()

    @classmethod
    def _load_env_from_license(cls, path):
        try:
            params = cls._load_params(path)
            env = gp.Env(params=params)
            print(f"Initialized Gurobi with {path}")
            return env
        except Exception as e:
            print(f"Gurobi initialization failed: {e}")
            return gp.Env()

    @classmethod
    def _load_params(cls, path):
        with open(path, "r") as f:
            params = json.load(f)
        if "LICENSEID" in params:
            params["LICENSEID"] = cls._try_int(params["LICENSEID"])
        return params

    @classmethod
    def _try_int(cls, val):
        try: return int(val)
        except (ValueError, TypeError): return val
