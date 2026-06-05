import re
from pathlib import Path
from u_utilities.u_shared import DenialConstraints, DenialConstraint, Predicate, Side
from .base import Loader

class DCsLoader(Loader):
    """
    Specialized loader for Denial Constraints (DCs).
    Parses DC text files into DenialConstraints objects.
    """
    _PREDICATE_OPERATORS = r"=|!=|<=|>=|<|>"
    _FIRST_TUPLE = r"t(\d+)\.([A-Za-z_]\w*)\s*"
    _SECOND_TUPLE = r"\s*t(\d+)\.([A-Za-z_]\w*)"
    _VALUE = r"([\'\"].*?[\'\"]|[-+]?\d+(?:\.\d+)?)"

    def load(self, path: Path) -> DenialConstraints:
        """Loads and parses DCs from a text file. Returns empty constraints if file missing."""
        if not path.exists():
            return DenialConstraints([])
        lines = path.read_text(encoding="utf-8").splitlines()
        constraints = [self._parse_dc(line) for line in lines if line.strip()]
        return DenialConstraints(constraints)
    
    def save(self, constraints: DenialConstraints, path: Path) -> None:
        """Saves DenialConstraints object to a text file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(constraints.to_string(), encoding="utf-8")

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
        binary_match = re.match(
            rf"^{self._FIRST_TUPLE}({self._PREDICATE_OPERATORS}){self._SECOND_TUPLE}$",
            raw_predicate,
        )
        if binary_match:
            return self._create_binary_predicate(binary_match)

        unary_match = re.match(
            rf"^{self._FIRST_TUPLE}({self._PREDICATE_OPERATORS})\s*{self._VALUE}$",
            raw_predicate,
        )
        if unary_match:
            return self._create_unary_predicate(unary_match)

        raise ValueError(f"Invalid predicate format: {raw_predicate}")

    def _create_binary_predicate(self, match):
        return Predicate(
            left=Side(attr=match.group(2), index=int(match.group(1)), is_value=False),
            opr=match.group(3),
            right=Side(attr=match.group(5), index=int(match.group(4)), is_value=False),
        )

    def _create_unary_predicate(self, match):
        return Predicate(
            left=Side(attr=match.group(2), index=int(match.group(1)), is_value=False),
            opr=match.group(3),
            right=Side(
                attr=match.group(4).strip("'\""),
                index=int(match.group(1)),
                is_value=True,
            ),
        )
