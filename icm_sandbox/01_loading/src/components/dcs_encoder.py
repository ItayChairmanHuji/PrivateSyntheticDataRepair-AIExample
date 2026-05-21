from src.entities.denial_constraints import DenialConstraints, DenialConstraint, Predicate, Side
from sklearn.preprocessing import LabelEncoder

class DCsEncoder:
    """Encodes literal values in Denial Constraints based on the data encoding mappings."""
    
    def encode(self, dcs: DenialConstraints, mappings: dict[str, LabelEncoder]) -> DenialConstraints:
        encoded_constraints = []
        for dc in dcs.constraints:
            encoded_constraints.append(self._encode_dc(dc, mappings))
        return DenialConstraints(encoded_constraints)

    def _encode_dc(self, dc: DenialConstraint, mappings: dict[str, LabelEncoder]) -> DenialConstraint:
        encoded_predicates = []
        for p in dc.predicates:
            encoded_predicates.append(self._encode_predicate(p, mappings))
        return DenialConstraint(encoded_predicates)

    def _encode_predicate(self, p: Predicate, mappings: dict[str, LabelEncoder]) -> Predicate:
        new_left = self._encode_side(p.left, mappings)
        new_right = self._encode_side(p.right, mappings)
        
        # If one side was encoded, we might need to handle the other side too if it's a value
        # Example: t1.City = 'NYC'
        # If 'City' is encoded, 'NYC' must be transformed to its numeric code.
        
        if p.left.is_value and not p.right.is_value and p.right.attr in mappings:
             new_left = self._encode_literal(p.left, mappings[p.right.attr])
        
        if p.right.is_value and not p.left.is_value and p.left.attr in mappings:
             new_right = self._encode_literal(p.right, mappings[p.left.attr])
             
        return Predicate(left=new_left, opr=p.opr, right=new_right)

    def _encode_side(self, side: Side, mappings: dict[str, LabelEncoder]) -> Side:
        # We don't necessarily encode the Side itself here if it's an attribute name,
        # but if it's a value, it depends on which attribute it's compared to.
        # This is handled in _encode_predicate for better context.
        return side

    def _encode_literal(self, side: Side, le: LabelEncoder) -> Side:
        try:
            # le.transform expects a list-like
            encoded_val = le.transform([str(side.attr)])[0]
            return Side(attr=encoded_val, index=side.index, is_value=True)
        except ValueError:
            # If the value is not in the encoder (unseen), we keep it as is or handle error.
            # In research framework, we trust it exists.
            return side
