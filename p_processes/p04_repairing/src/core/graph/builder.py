from __future__ import annotations

from u_utilities.u_shared import ViolationSet
from .initializer import GraphBuilder


class ConflictGraphBuilder:
    @staticmethod
    def build(n: int, violation_set: ViolationSet):
        return GraphBuilder(n, violation_set).graph
