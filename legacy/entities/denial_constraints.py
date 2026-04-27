import random
from dataclasses import dataclass

from src.denial_constraints.entities.denial_constraint import DenialConstraint


@dataclass
class DenialConstraints:
    constraints: list[DenialConstraint]

    @property
    def attrs(self) -> set[str]:
        return set().union(*(dc.attrs for dc in self.constraints))

    def select_randomly(self) -> DenialConstraint:
        return random.choice(self.constraints)
