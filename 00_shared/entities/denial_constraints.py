from dataclasses import dataclass

@dataclass
class Side:
    attr: str
    index: int
    is_value: bool

@dataclass
class Predicate:
    left: Side
    opr: str
    right: Side

    @property
    def is_unary(self) -> bool:
        return self.left.index == self.right.index

    @property
    def attrs(self) -> set[str]:
        attrs = set()
        if not self.left.is_value:
            attrs.add(self.left.attr)
        if not self.right.is_value:
            attrs.add(self.right.attr)
        return attrs

    def to_string(self) -> str:
        return f"{self._format_side(self.left)} {self.opr} {self._format_side(self.right)}"

    def _format_side(self, s: Side) -> str:
        if s.is_value:
            if isinstance(s.attr, str) and (s.attr.startswith("'") or s.attr.startswith('"')):
                return s.attr
            try:
                float(s.attr)
                return str(s.attr)
            except ValueError:
                return f"'{s.attr}'"
        return f"t{s.index}.{s.attr}"
    
@dataclass
class DenialConstraint:
    predicates: list[Predicate]

    @property
    def attrs(self) -> set[str]:
        return set().union(*(p.attrs for p in self.predicates))

    def to_string(self) -> str:
        return "not(" + " & ".join(p.to_string() for p in self.predicates) + ")"

@dataclass
class DenialConstraints:
    constraints: list[DenialConstraint]

    @property
    def attrs(self) -> set[str]:
        return set().union(*(dc.attrs for dc in self.constraints))
