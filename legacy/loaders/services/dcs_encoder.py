from typing import Any

from src.entities.denial_constraints import DenialConstraints


def _strip_quotes(value: str) -> str:
    return value.replace('"', "").replace("'", "")


def _coerce_literal(attr: str, raw: str, mapping: dict[str, Any]) -> Any:
    raw_value = _strip_quotes(raw)
    return mapping[attr][raw_value] if attr in mapping else raw_value


def encode_dcs(dcs: DenialConstraints, mapping: dict[str, Any]) -> DenialConstraints:
    for dc in dcs.constraints:
        for predicate in dc.predicates:
            if predicate.left.is_value:
                predicate.left.attr = _coerce_literal(
                    predicate.right.attr,
                    str(predicate.left.attr),
                    mapping,
                )
            if predicate.right.is_value:
                predicate.right.attr = _coerce_literal(
                    predicate.left.attr,
                    str(predicate.right.attr),
                    mapping,
                )
    return dcs
