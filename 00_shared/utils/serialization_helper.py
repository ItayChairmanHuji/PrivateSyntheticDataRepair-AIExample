import numpy as np

def get_serializable_params(obj):
    """
    Recursively extracts serializable parameters from an object.
    Handles numpy arrays and nested objects.
    """
    params = {}
    # If it's a dict, just process its values
    if isinstance(obj, dict):
        for k, v in obj.items():
            params[k] = _process_value(v)
        return params
        
    # If it has __dict__, process it
    for k, v in getattr(obj, '__dict__', {}).items():
        if k.startswith('_'):  # Skip private members
            continue
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
