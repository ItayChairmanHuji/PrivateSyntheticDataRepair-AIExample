import random
from entities.dataset import Dataset

def run_co_noise(dataset: Dataset) -> Dataset:
    dc = dataset.dcs.select_randomly()
    t1, t2 = _sample_tuples(dataset)
    
    # We use 1-based indexing for data because Predicate.eval uses [None, t1, t2]
    data = [None, t1, t2]
    
    for pred in dc.predicates:
        if not pred.eval(t1, t2):
            _satisfy_predicate(pred, t1, t2, data)
    
    dataset.data.loc[t1['index']] = t1.drop('index')
    dataset.data.loc[t2['index']] = t2.drop('index')
    return dataset

def _sample_tuples(dataset: Dataset) -> tuple:
    # reset_index adds 'index' column which stores original row index
    data = dataset.data.sample(n=2).reset_index()
    return data.iloc[0], data.iloc[1]

def _satisfy_predicate(pred, t1, t2, data):
    # Determine which side to modify. If it's a value comparison, we must modify the attribute side.
    # If both sides are tuples, we randomly choose one to modify.
    if pred.right_is_value:
        modify_left = True
    elif pred.left.is_value:
        modify_left = False
    else:
        modify_left = random.choice([True, False])

    if modify_left:
        target = data[pred.left_tuple]
        val_to_match = pred._side_value(data[pred.right_tuple], pred.right)
        attr = pred.left.attr
        opr = pred.opr
    else:
        target = data[pred.right_tuple]
        val_to_match = pred._side_value(data[pred.left_tuple], pred.left)
        attr = pred.right.attr
        opr = _invert_operator(pred.opr)

    target_type = type(target[attr])
    if pred.uses_literal_value:
        val_to_match = _convert_value(val_to_match, target_type)

    if opr == "=":
        target[attr] = val_to_match
    elif opr == "!=":
        if target[attr] == val_to_match:
            target[attr] = _get_different_value(val_to_match, target_type)
    elif opr == "<":
        target[attr] = _get_smaller_value(val_to_match, target_type)
    elif opr == "<=":
        target[attr] = val_to_match
    elif opr == ">":
        target[attr] = _get_greater_value(val_to_match, target_type)
    elif opr == ">=":
        target[attr] = val_to_match

def _invert_operator(opr: str) -> str:
    return {
        ">": "<",
        "<": ">",
        ">=": "<=",
        "<=": ">=",
        "=": "=",
        "!=": "!=",
    }[opr]

def _convert_value(val, target_type):
    if isinstance(val, str):
        val = val.strip("'").strip('"')
    try:
        # Special handling for numeric-ish types
        if target_type in [int, float] or "int" in str(target_type) or "float" in str(target_type):
            return target_type(float(val))
        return target_type(val)
    except:
        return val

def _get_different_value(val, target_type):
    if "int" in str(target_type) or "float" in str(target_type):
        return target_type(val + 1)
    return str(val) + "_"

def _get_smaller_value(val, target_type):
    if "int" in str(target_type) or "float" in str(target_type):
        return target_type(val - 1)
    return val

def _get_greater_value(val, target_type):
    if "int" in str(target_type) or "float" in str(target_type):
        return target_type(val + 1)
    return val
