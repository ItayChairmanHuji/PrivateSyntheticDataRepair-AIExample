import re
from pathlib import Path

from denial_constraints.entities.denial_constraint import DenialConstraint
from src.entities.denial_constraints import DenialConstraints
from denial_constraints.entities.predicate import Predicate, Side

_PREDICATE_OPERATORS = r"=|!=|<=|>=|<|>"
_FIRST_TUPLE = r"t(\d+)\.([A-Za-z_]\w*)\s*"
_SECOND_TUPLE = r"\s*t(\d+)\.([A-Za-z_]\w*)"
_VALUE = r"([\'\"].*?[\'\"]|[-+]?\d+(?:\.\d+)?)"


def _get_raw_predicates(constraints_string: str) -> list[str]:
    normalized = constraints_string.strip()
    contains_not = normalized.startswith("not(") and normalized.endswith(")")
    constraints_string = normalized[4:-1] if contains_not else normalized
    return [p.strip() for p in constraints_string.split("&") if p.strip()]


def _two_tuples_regex():
    return re.compile(rf"^{_FIRST_TUPLE}({_PREDICATE_OPERATORS}){_SECOND_TUPLE}$")


def _right_unary_regex():
    return re.compile(rf"^{_FIRST_TUPLE}({_PREDICATE_OPERATORS})\s*{_VALUE}$")


def _left_unary_regex():
    return re.compile(rf"^{_VALUE}({_PREDICATE_OPERATORS})\s*t(\d+)\.([A-Za-z_]\w*)$")


def _invert_operator(opr: str) -> str:
    return {
        ">": "<",
        "<": ">",
        ">=": "<=",
        "<=": ">=",
        "=": "=",
        "!=": "!=",
    }[opr]


def _extract_regex(match, right_is_value, invert_opr):
    if not right_is_value:
        return match.group(2), match.group(3), match.group(5)
    elif not invert_opr:
        return match.group(2), match.group(3), match.group(4)
    return match.group(4), _invert_operator(match.group(2)), match.group(1)


def _extract_tuples(match, right_is_value, invert_opr):
    if not right_is_value:
        return int(match.group(1)), int(match.group(4))
    if not invert_opr:
        tuple_id = int(match.group(1))
        return tuple_id, tuple_id
    tuple_id = int(match.group(3))
    return tuple_id, tuple_id


def _build_predicate(attr1, opr, attr2, left_tuple, right_tuple, right_is_value):
    left = Side(attr=attr1, index=left_tuple, is_value=False)
    right = Side(attr=attr2, index=right_tuple, is_value=right_is_value)
    return Predicate(
        left=left,
        opr=opr,
        right=right,
    )


def _predicate_matchers():
    return [
        (_two_tuples_regex(), False, False),
        (_right_unary_regex(), True, False),
        (_left_unary_regex(), True, True),
    ]


def _normalize_predicate(predicate: Predicate) -> Predicate:
    if predicate.is_unary:
        return predicate

    if predicate.left_tuple == 1 and predicate.right_tuple == 2:
        return predicate

    if predicate.left_tuple == 2 and predicate.right_tuple == 1:
        return Predicate(
            left=Side(
                attr=predicate.right.attr,
                index=1,
                is_value=predicate.right.is_value,
            ),
            opr=_invert_operator(predicate.opr),
            right=Side(
                attr=predicate.left.attr,
                index=2,
                is_value=predicate.left.is_value,
            ),
        )

    return predicate


def _parse_predicate(raw_predicate: str) -> Predicate:
    for regex, is_value, invert in _predicate_matchers():
        match = regex.match(raw_predicate)
        if match is not None:
            attr1, opr, attr2 = _extract_regex(
                match, right_is_value=is_value, invert_opr=invert
            )
            left_tuple, right_tuple = _extract_tuples(
                match, right_is_value=is_value, invert_opr=invert
            )
            return _build_predicate(
                attr1,
                opr,
                attr2,
                left_tuple=left_tuple,
                right_tuple=right_tuple,
                right_is_value=is_value,
            )
    raise ValueError(f"Invalid predicate format: {raw_predicate}")


def parse_dc(constraint: str) -> DenialConstraint:
    raw_predicates = _get_raw_predicates(constraint)
    predicates = [_normalize_predicate(_parse_predicate(p)) for p in raw_predicates]
    return DenialConstraint(predicates)


def load_dcs(path: str | Path):
    dcs_path = Path(path)
    lines = dcs_path.read_text(encoding="utf-8").splitlines()
    constraints = [parse_dc(line) for line in lines if line.strip()]
    return DenialConstraints(constraints)
