import abc


class BaseSemanticError(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def message(self) -> str:
        pass


class UndefinedVariableError(BaseSemanticError):
    def __init__(self, lexim, lineno):
        self.lexim = lexim
        self.lineno = lineno

    def message(self) -> str:
        return f"#{self.lineno + 1} : Semantic Error! '{self.lexim}' is not defined appropriately."


class UnmatchedContinueError(BaseSemanticError):
    def __init__(self, lineno):
        self.lineno = lineno

    def message(self) -> str:
        return f"#{self.lineno + 1} : Semantic Error! No 'while' found for 'continue'."


class UnmatchedWhileError(BaseSemanticError):
    def __init__(self, lineno):
        self.lineno = lineno

    def message(self) -> str:
        return f"#{self.lineno + 1} : Semantic Error! No 'while' found for 'break'."
