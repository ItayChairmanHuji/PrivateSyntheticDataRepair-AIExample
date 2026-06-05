import re
from pathlib import Path
from .loader import Loader
from u_utilities.u_shared import (
    DenialConstraint,
    DenialConstraints,
    Predicate,
    Side,
)


class DCsLoader(Loader):
    _OPERATORS = r"=|!=|<=|>=|<|>"
    _T1 = r"t(\d+)\.([A-Za-z_]\w*)\s*"
    _T2 = r"\s*t(\d+)\.([A-Za-z_]\w*)"
    _VAL = r"([\'\"].*?[\'\"]|[-+]?\d+(?:\.\d+)?)"

    def load(self, path: str | Path) -> DenialConstraints:
        content = Path(path).read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        return DenialConstraints([self._parse_dc(line) for line in lines])

    def _parse_dc(self, constraint: str) -> DenialConstraint:
        raw_predicates = self._get_raw_predicates(constraint)
        return DenialConstraint([self._parse_predicate(p) for p in raw_predicates])

    def _get_raw_predicates(self, dc_string: str) -> list[str]:
        clean = dc_string.strip()
        if clean.startswith("not(") and clean.endswith(")"):
            clean = clean[4:-1]
        return [p.strip() for p in clean.split("&") if p.strip()]

    def _parse_predicate(self, raw: str) -> Predicate:
        if match := self._match_binary(raw):
            return self._create_binary(match)
        if match := self._match_unary(raw):
            return self._create_unary(match)
        raise ValueError(f"Invalid predicate: {raw}")

    def _match_binary(self, raw: str) -> re.Match | None:
        pattern = rf"^{self._T1}({self._OPERATORS}){self._T2}$"
        return re.match(pattern, raw)

    def _match_unary(self, raw: str) -> re.Match | None:
        pattern = rf"^{self._T1}({self._OPERATORS})\s*{self._VAL}$"
        return re.match(pattern, raw)

    def _create_binary(self, m: re.Match) -> Predicate:
        return Predicate(
            left=Side(attr=m.group(2), index=int(m.group(1)), is_value=False),
            opr=m.group(3),
            right=Side(attr=m.group(5), index=int(m.group(4)), is_value=False),
        )

    def _create_unary(self, m: re.Match) -> Predicate:
        return Predicate(
            left=Side(attr=m.group(2), index=int(m.group(1)), is_value=False),
            opr=m.group(3),
            right=Side(attr=m.group(4).strip("'\""), index=int(m.group(1)), is_value=True),
        )
