from dataclasses import dataclass, field
from enum import Enum, auto

from u_utilities.u_shared import DenialConstraint, Predicate


class ConstraintType(Enum):
    FD = auto()
    CONDITIONAL_CONSTANT = auto()
    SINGLE_ORDER = auto()
    TWO_ORDER = auto()
    GENERAL = auto()


@dataclass
class ConstraintProfile:
    type: ConstraintType
    equality_attrs: list[str] = field(default_factory=list)
    inequality_attrs: list[str] = field(default_factory=list)
    order_attrs: list[str] = field(default_factory=list)
    unary_predicates: list[Predicate] = field(default_factory=list)
    binary_predicates: list[Predicate] = field(default_factory=list)
    t1_unary: list[Predicate] = field(default_factory=list)
    t2_unary: list[Predicate] = field(default_factory=list)


class ConstraintAnalyzer:
    def analyze(self, dc: DenialConstraint) -> ConstraintProfile:
        binary = [p for p in dc.predicates if not p.is_unary]
        unary = [p for p in dc.predicates if p.is_unary]
        t1_unary, t2_unary = self._split_unary(unary)
        eq_attrs = self._attrs_for(binary, ("=", "=="))
        neq_attrs = self._attrs_for(binary, ("!=", "<>"))
        order_preds = [p for p in binary if self._is_order_predicate(p)]
        c_type = self._classify(eq_attrs, neq_attrs, order_preds, t1_unary, t2_unary)
        return self._profile(c_type, eq_attrs, neq_attrs, order_preds, binary, unary)

    def _profile(self, c_type, eq_attrs, neq_attrs, order_preds, binary, unary):
        t1_unary, t2_unary = self._split_unary(unary)
        return ConstraintProfile(
            type=c_type,
            equality_attrs=eq_attrs,
            inequality_attrs=neq_attrs,
            order_attrs=[p.left.attr for p in order_preds],
            unary_predicates=unary,
            binary_predicates=order_preds if self._is_order_type(c_type) else binary,
            t1_unary=t1_unary,
            t2_unary=t2_unary,
        )

    def _classify(self, eq_attrs, neq_attrs, order_preds, t1_unary, t2_unary):
        match (bool(order_preds), len(neq_attrs), len(order_preds)):
            case (False, 1, _):
                return self._fd_type(t1_unary, t2_unary)
            case (True, 0, 1) if not eq_attrs:
                return ConstraintType.SINGLE_ORDER
            case (True, 0, 2) if not eq_attrs:
                return ConstraintType.TWO_ORDER
            case _:
                return ConstraintType.GENERAL

    def _fd_type(self, t1_unary, t2_unary) -> ConstraintType:
        return ConstraintType.CONDITIONAL_CONSTANT if t1_unary or t2_unary else ConstraintType.FD

    def _attrs_for(self, predicates: list[Predicate], operators: tuple[str, ...]) -> list[str]:
        return [p.left.attr for p in predicates if self._is_same_attr(p, operators)]

    def _is_order_predicate(self, predicate: Predicate) -> bool:
        return self._is_same_attr(predicate, (">", ">=", "<", "<="))

    def _is_same_attr(self, predicate: Predicate, operators: tuple[str, ...]) -> bool:
        return predicate.opr in operators and predicate.left.attr == predicate.right.attr

    def _is_order_type(self, c_type: ConstraintType) -> bool:
        return c_type in (ConstraintType.SINGLE_ORDER, ConstraintType.TWO_ORDER)

    def _split_unary(self, predicates: list[Predicate]) -> tuple[list[Predicate], list[Predicate]]:
        return (
            [p for p in predicates if p.left.index == 1],
            [p for p in predicates if p.left.index == 2],
        )
