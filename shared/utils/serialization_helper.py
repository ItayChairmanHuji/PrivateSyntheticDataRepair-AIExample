import numpy as np

def get_serializable_params(obj):
    if isinstance(obj, dict):
        return {k: _process_value(v) for k, v in obj.items()}
    
    params = {}
    for k, v in getattr(obj, '__dict__', {}).items():
        if not k.startswith('_'):
            params[k] = _process_value(v)
    return params

def _process_value(v):
    if isinstance(v, (int, float, str, bool, list, dict)) or v is None:
        return v
    elif isinstance(v, np.ndarray):
        return v.tolist()
    elif hasattr(v, '__dict__'):
        return get_serializable_params(v)
    return str(v)
