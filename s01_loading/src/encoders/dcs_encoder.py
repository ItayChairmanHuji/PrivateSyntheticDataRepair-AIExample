from dataclasses import dataclass
from sklearn.preprocessing import LabelEncoder
from shared.entities.denial_constraints import (
    DenialConstraint,
    DenialConstraints,
    Predicate,
    Side,
)

@dataclass
class DCsEncoder:
    def encode(
        self, dcs: DenialConstraints, mappings: dict[str, LabelEncoder]
    ) -> DenialConstraints:
        encoded_constraints = [self._encode_dc(dc, mappings) for dc in dcs.constraints]
        return DenialConstraints(encoded_constraints)

    def _encode_dc(
        self, dc: DenialConstraint, mappings: dict[str, LabelEncoder]
    ) -> DenialConstraint:
        encoded_predicates = [
            self._encode_predicate(p, mappings) for p in dc.predicates
        ]
        return DenialConstraint(encoded_predicates)

    def _encode_predicate(
        self, p: Predicate, mappings: dict[str, LabelEncoder]
    ) -> Predicate:
        new_left, new_right = self._handle_value_encoding(p, p.left, p.right, mappings)
        return Predicate(left=new_left, opr=p.opr, right=new_right)

    def _handle_value_encoding(self, p, new_left, new_right, mappings):
        if p.left.is_value and not p.right.is_value and p.right.attr in mappings:
            new_left = self._encode_literal(p.left, mappings[p.right.attr])

        if p.right.is_value and not p.left.is_value and p.left.attr in mappings:
            new_right = self._encode_literal(p.right, mappings[p.left.attr])

        return new_left, new_right

    def _encode_literal(self, side: Side, le: LabelEncoder) -> Side:
        try:
            encoded_val = le.transform([str(side.attr)])[0]
            return Side(attr=encoded_val, index=side.index, is_value=True)
        except ValueError:
            return side
