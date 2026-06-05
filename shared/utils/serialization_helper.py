import numpy as np
import json

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NpEncoder, self).default(obj)

def get_serializable_params(obj):
    if isinstance(obj, (int, float, str, bool, list, dict)) or obj is None:
        return _process_value(obj)
    
    params = {}
    for k, v in getattr(obj, '__dict__', {}).items():
        if not k.startswith('_'):
            params[k] = _process_value(v)
    return params

def _process_value(v):
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return float(v)
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, np.ndarray):
        return v.tolist()
    
    if isinstance(v, list):
        return [_process_value(item) for item in v]
    if isinstance(v, dict):
        return {str(k): _process_value(val) for k, val in v.items()}
    
    if hasattr(v, '__dict__'):
        return get_serializable_params(v)
    
    # Check for basic types
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
        
    return str(v)
