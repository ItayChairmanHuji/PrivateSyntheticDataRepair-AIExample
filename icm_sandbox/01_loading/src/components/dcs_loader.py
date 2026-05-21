import re
from pathlib import Path
from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side

class DCsLoader:
    """
    Parses Denial Constraints from text files.
    Supports formats like 'not(t1.A=t2.A & t1.B!=t2.B)' or simple unary 't1.A=v'.
    """
    _PREDICATE_OPERATORS = r"=|!=|<=|>=|<|>"
    _FIRST_TUPLE = r"t(\d+)\.([A-Za-z_]\w*)\s*"
    _SECOND_TUPLE = r"\s*t(\d+)\.([A-Za-z_]\w*)"
    _VALUE = r"([\'\"].*?[\'\"]|[-+]?\d+(?:\.\d+)?)"

    def load(self, path: str | Path) -> DenialConstraints:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
        constraints = [self._parse_dc(line) for line in lines if line.strip()]
        return DenialConstraints(constraints)

    def _parse_dc(self, constraint: str) -> DenialConstraint:
        raw_predicates = self._get_raw_predicates(constraint)
        predicates = [self._parse_predicate(p) for p in raw_predicates]
        return DenialConstraint(predicates)

    def _get_raw_predicates(self, constraints_string: str) -> list[str]:
        normalized = constraints_string.strip()
        if normalized.startswith("not(") and normalized.endswith(")"):
            normalized = normalized[4:-1]
        return [p.strip() for p in normalized.split("&") if p.strip()]

    def _parse_predicate(self, raw_predicate: str) -> Predicate:
        # Two tuples: t1.A = t2.B
        match = re.match(rf"^{self._FIRST_TUPLE}({self._PREDICATE_OPERATORS}){self._SECOND_TUPLE}$", raw_predicate)
        if match:
            return Predicate(
                left=Side(attr=match.group(2), index=int(match.group(1)), is_value=False),
                opr=match.group(3),
                right=Side(attr=match.group(5), index=int(match.group(4)), is_value=False)
            )
        
        # Right unary: t1.A = "value"
        match = re.match(rf"^{self._FIRST_TUPLE}({self._PREDICATE_OPERATORS})\s*{self._VALUE}$", raw_predicate)
        if match:
            return Predicate(
                left=Side(attr=match.group(2), index=int(match.group(1)), is_value=False),
                opr=match.group(3),
                right=Side(attr=match.group(4).strip("'\""), index=int(match.group(1)), is_value=True)
            )
        
        raise ValueError(f"Invalid predicate format: {raw_predicate}")
