from dataclasses import dataclass
from enum import Enum
from string import ascii_letters, digits, whitespace, printable
from typing import List, Union

KEYWORDS = ['break', 'continue', 'def', 'else', 'if', 'return', 'while']
EPSILON = 'epsilon'


class TokenType(Enum):
    NUM = 0
    ID = 1
    KEYWORD = 2
    SYMBOL = 3
    COMMENT = 4
    WHITESPACE = 5
    EOF = 6


class NonTerminal(Enum):
    Program = 0
    Statements = 1
    Statement = 2
    Simple_stmt = 3
    Compound_stmt = 4
    Assignment_Call = 5
    B = 6
    C = 7
    List_Rest = 8
    Return_stmt = 9
    Return_Value = 10
    Global_stmt = 11
    Function_def = 12
    Params = 13
    Params_Prime = 14
    If_stmt = 15
    Else_block = 16
    Iteration_stmt = 17
    Relational_Expression = 18
    Relop = 19
    Expression = 20
    Expression_Prime = 21
    Term = 22
    Term_Prime = 23
    Factor = 24
    Power = 25
    Primary = 26
    Arguments = 27
    Arguments_Prime = 28
    Atom = 29


class Terminal(Enum):
    Semicolon = 0  # ;
    Break = 1
    Continue = 2
    ID = 3
    EqualSign = 4  # =
    BracketOpen = 5  # [
    BracketsClose = 6  # ]
    ParenthesesOpen = 7  # (
    ParenthesesClose = 8  # )
    Comma = 9  # ,
    Return = 10
    Global = 11
    Def = 12
    Colon = 13  # :
    If = 14
    Else = 15
    While = 16
    DoubleEqualSign = 17  # ==
    SmallerSign = 18  # <
    PlusSign = 19  # +
    MinusSign = 20  # -
    StarSign = 21  #
    DoubleStarSign = 22  # **
    NUM = 23
    epsilon = 24  # ε


class Char:
    LETTER = ascii_letters
    DIGIT = digits
    WHITESPACE = whitespace
    SYMBOL = '()[]:*+-=;,<'
    COMMENT_SYMBOL = '/#'
    ALL = printable
    EOF = chr(3)


class ActionSymbols(Enum):
    PID = 0
    PNUM = 1
    MULT = 2
    ADD = 3
    SUB = 4
    ASSIGN = 5
    SaveRelop = 6
    RelopAct = 7
    # if statement
    JFalse = 8
    JTrue = 9
    Endif = 10
    JHere = 11

    # while statement:
    StartLoop = 12
    CheckCond = 13
    EndLoop = 14
    LoopBreak = 15
    LoopContinue = 16

    # function statement:
    FuncDef = 17
    FuncPID = 18
    FuncEnd = 19
    FuncCallStart = 20
    FuncCallEnd = 21
    FuncSaveArgs = 22
    FuncStoreRV = 23
    FuncJBack = 24
    FuncCallEnd2 = 25


class AddrCode(Enum):
    ADD = 1
    MULT = 2
    SUB = 3
    EQ = 4


@dataclass
class TokenPack:
    lineno: int
    token_type: TokenType
    lexim: str


@dataclass
class ListData:
    pass


@dataclass
class FunctionData:
    addr: int
    ra: int
    rv: int
    args: List[int]


@dataclass
class SymbolTableItem:
    lexim: str
    addr: int
    type: Union[FunctionData, ListData, None]
    scope: int


@dataclass
class SymbolTable:
    items: List[SymbolTableItem]
