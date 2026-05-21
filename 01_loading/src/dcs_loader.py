import re
from pathlib import Path
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

_PREDICATE_OPERATORS = r"=|!=|<=|>=|<|>"
_FIRST_TUPLE = r"t(\d+)\.([A-Za-z_]\w*)\s*"
_SECOND_TUPLE = r"\s*t(\d+)\.([A-Za-z_]\w*)"
_VALUE = r"([\'\"].*?[\'\"]|[-+]?\d+(?:\.\d+)?)"

def _get_raw_predicates(constraints_string: str) -> list[str]:
    normalized = constraints_string.strip()
    if normalized.startswith("not(") and normalized.endswith(")"):
        normalized = normalized[4:-1]
    return [p.strip() for p in normalized.split("&") if p.strip()]

def _parse_predicate(raw_predicate: str) -> Predicate:
    # Two tuples: t1.A = t2.B
    match = re.match(rf"^{_FIRST_TUPLE}({_PREDICATE_OPERATORS}){_SECOND_TUPLE}$", raw_predicate)
    if match:
        return Predicate(
            left=Side(attr=match.group(2), index=int(match.group(1)), is_value=False),
            opr=match.group(3),
            right=Side(attr=match.group(5), index=int(match.group(4)), is_value=False)
        )
    
    # Right unary: t1.A = "value"
    match = re.match(rf"^{_FIRST_TUPLE}({_PREDICATE_OPERATORS})\s*{_VALUE}$", raw_predicate)
    if match:
        return Predicate(
            left=Side(attr=match.group(2), index=int(match.group(1)), is_value=False),
            opr=match.group(3),
            right=Side(attr=match.group(4).strip("'\""), index=int(match.group(1)), is_value=True)
        )
    
    raise ValueError(f"Invalid predicate format: {raw_predicate}")

def parse_dc(constraint: str) -> DenialConstraint:
    raw_predicates = _get_raw_predicates(constraint)
    predicates = [_parse_predicate(p) for p in raw_predicates]
    return DenialConstraint(predicates)

def load_dcs(path: str | Path) -> DenialConstraints:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    constraints = [parse_dc(line) for line in lines if line.strip()]
    return DenialConstraints(constraints)
