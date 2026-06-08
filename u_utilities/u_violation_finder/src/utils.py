from collections.abc import Callable
from numbers import Number

import numpy as np
import pandas as pd

from u_utilities.u_shared import Predicate


OPERATORS: dict[str, Callable[[pd.Series, object], pd.Series]] = {
    ">": lambda left, right: left > right,
    ">=": lambda left, right: left >= right,
    "<": lambda left, right: left < right,
    "<=": lambda left, right: left <= right,
}


def apply_unary_predicates(df: pd.DataFrame, predicates: list[Predicate]) -> np.ndarray:
    mask = np.ones(len(df), dtype=bool)
    for predicate in predicates:
        mask &= evaluate_unary(df, predicate).to_numpy()
    return mask


def evaluate_unary(df: pd.DataFrame, predicate: Predicate) -> pd.Series:
    left = df[predicate.left.attr]
    right = _right_operand(df, predicate)
    left, right = _align_numeric_literal(left, right)
    match predicate.opr:
        case "=" | "==":
            return left.eq(right) | (left.isna() & pd.isna(right))
        case "!=" | "<>":
            return left.ne(right) & ~(left.isna() & pd.isna(right))
        case operator:
            return OPERATORS[operator](_coerce_numeric(left), _coerce_numeric(right))


def _right_operand(df: pd.DataFrame, predicate: Predicate):
    if not predicate.right.is_value:
        return df[predicate.right.attr]
    return _coerce_literal(predicate.right.attr)


def _coerce_literal(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _coerce_numeric(value):
    if isinstance(value, pd.Series):
        return pd.to_numeric(value, errors="coerce")
    return value


def _align_numeric_literal(left: pd.Series, right):
    if isinstance(right, Number) and not isinstance(right, bool):
        return pd.to_numeric(left, errors="coerce"), right
    return left, right
