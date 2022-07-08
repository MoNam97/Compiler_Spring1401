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
        return f"#{self.lineno + 1} : Semantic Error! " \
               f"'{self.lexim}' is not defined appropriately."


class MismatchedArgumentsError(BaseSemanticError):
    def __init__(self, func_lexim, lineno):
        self.func_lexim = func_lexim
        self.lineno = lineno

    def message(self) -> str:
        return f"#{self.lineno + 1} : Semantic Error! " \
               f"Mismatch in numbers of arguments of '{self.func_lexim}'."


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


class VoidOperandError(BaseSemanticError):
    def __init__(self, lineno):
        self.lineno = lineno

    def message(self) -> str:
        return f"#{self.lineno + 1} : Semantic Error! Void type in operands."


class MainNotFoundError(BaseSemanticError):
    def __init__(self, lineno):
        self.lineno = lineno

    def message(self) -> str:
        return f"#{self.lineno + 1} : Semantic Error! main function not found."


class FunctionOverloadError(BaseSemanticError):
    def __init__(self, lexim, lineno):
        self.lexim = lexim
        self.lineno = lineno

    def message(self) -> str:
        return f"#{self.lineno + 1} : Semantic Error!" \
               f" Function '{self.lexim}' has already been defined with this number of arguments."
