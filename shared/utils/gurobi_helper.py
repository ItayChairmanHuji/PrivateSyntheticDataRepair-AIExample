import gurobipy as gp
import json
import os

class GurobiHelper:
    _env = None

    @classmethod
    def get_env(cls):
        if cls._env is None:
            license_path = "license.json"
            if os.path.exists(license_path):
                try:
                    with open(license_path, "r") as f:
                        params = json.load(f)
                    
                    # Fix: Gurobi expects LICENSEID to be an integer
                    if "LICENSEID" in params and isinstance(params["LICENSEID"], str):
                        try:
                            params["LICENSEID"] = int(params["LICENSEID"])
                        except ValueError:
                            pass

                    cls._env = gp.Env(params=params)
                    print(f"Successfully initialized Gurobi environment with {license_path}")
                except Exception as e:
                    print(f"Failed to initialize Gurobi environment with license file: {e}")
                    cls._env = gp.Env()
            else:
                cls._env = gp.Env()
        return cls._env
