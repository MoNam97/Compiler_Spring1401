from enum import Enum

IDENTIFIERS = ['break', 'continue', 'def', 'else', 'if', 'return', 'while']


class TokenType(Enum):
    NUMBER = 0
    ID = 1
    KEYWORD = 2
    SYMBOL = 3
    COMMENT = 4
    WHITESPACE = 5
