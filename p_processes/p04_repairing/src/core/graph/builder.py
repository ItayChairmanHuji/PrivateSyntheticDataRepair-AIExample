from __future__ import annotations

from u_utilities.u_shared import ViolationSet


class ConflictGraphBuilder:
    @staticmethod
    def build(n: int, violation_set: ViolationSet):
        from .graph import Graph

        return Graph(n, violation_set)
