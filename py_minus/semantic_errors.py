import abc


class BaseSemanticError(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def message(self) -> str:
        pass


class UndefinedVariableError(BaseSemanticError):
    def __init__(self, lexim):
        self.lexim = lexim

    def message(self) -> str:
        return f"#11 : Semantic Error! '{self.lexim}' is not defined appropriately."
