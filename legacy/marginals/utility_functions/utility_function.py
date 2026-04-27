from abc import abstractmethod, ABC

from pandas import DataFrame


class UtilityFunction(ABC):
    @abstractmethod
    def __call__(self, p_marg, s_marg):
        raise NotImplementedError("Utility function not implemented")

    @abstractmethod
    def sensitivity(self, data: DataFrame):
        raise NotImplementedError("Sensitivity not implemented")