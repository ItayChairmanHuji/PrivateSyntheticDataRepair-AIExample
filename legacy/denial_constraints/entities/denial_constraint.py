from dataclasses import dataclass

from denial_constraints.entities.predicate import Predicate


@dataclass
class DenialConstraint:
    predicates: list[Predicate]

    @property
    def attrs(self) -> set[str]:
        return set().union(*(p.attrs for p in self.predicates))

    @property
    def unary_predicates(self) -> list[Predicate]:
        return [predicate for predicate in self.predicates if predicate.is_unary]

    @property
    def cross_predicates(self) -> list[Predicate]:
        return [predicate for predicate in self.predicates if predicate.is_cross_tuple]

    def predicates_for_tuple(self, tuple_index: int) -> list[Predicate]:
        tuple_id = tuple_index + 1
        return [
            predicate
            for predicate in self.unary_predicates
            if predicate.left_tuple == tuple_id
        ]

