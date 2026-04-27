from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame

from denial_constraints.loading.value_formatter import format_value

OPRS = {
    "=": lambda x, y: x == y,
    "<": lambda x, y: x < y,
    ">": lambda x, y: x > y,
    "<=": lambda x, y: x <= y,
    ">=": lambda x, y: x >= y,
    "!=": lambda x, y: x != y,
}


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
    def left_tuple(self) -> int:
        return self.left.index

    @property
    def right_tuple(self) -> int:
        return self.right.index

    @property
    def attr1(self) -> str:
        return self.left.attr

    @property
    def attr2(self) -> str:
        return self.right.attr

    @property
    def right_is_value(self) -> bool:
        return self.right.is_value

    @property
    def sides(self) -> list[Side]:
        return [self.left, self.right]

    @property
    def is_unary(self) -> bool:
        return self.left.index == self.right.index

    @property
    def is_cross_tuple(self) -> bool:
        return not self.is_unary

    @property
    def uses_literal_value(self) -> bool:
        return self.left.is_value or self.right.is_value

    def eval(self, t1: DataFrame = None, t2: DataFrame = None) -> pd.Series | bool:
        data = self._data_for_eval(t1, t2)
        left = self._side_value(data[self.left.index], self.left)
        right = self._side_value(data[self.right.index], self.right)
        return OPRS[self.opr](left, right)

    @staticmethod
    def _data_for_eval(t1, t2):
        if t1 is not None and t2 is not None:
            return [None, t1, t2]
        val = t1 if t1 is not None else t2
        if val is not None:
            return [None, val, val]
        raise ValueError("At least one of t1 or t2 must be provided")

    def _side_value(self, data: DataFrame, side: Side):
        return side.attr if side.is_value else data[side.attr]

    @property
    def sql(self) -> str:
        right_side = (
            format_value(self.right.attr)
            if self.right_is_value
            else f"t{self.right_tuple}.{self.right.attr}"
        )
        left_side = (
            format_value(self.left.attr)
            if self.left.is_value
            else f"t{self.left_tuple}.{self.left.attr}"
        )
        return f"{left_side} {self.opr} {right_side}"

    @property
    def attrs(self) -> set[str]:
        attrs = {side.attr for side in self.sides if not side.is_value}
        return attrs
