from enum import Enum
from string import ascii_letters, digits, whitespace, printable

KEYWORDS = ['break', 'continue', 'def', 'else', 'if', 'return', 'while']


class TokenType(Enum):
    NUMBER = 0
    ID = 1
    KEYWORD = 2
    SYMBOL = 3
    COMMENT = 4
    WHITESPACE = 5
    EOF = 6

#class Non_Terminal(Enum):


class Char:
    LETTER = ascii_letters
    DIGIT = digits
    WHITESPACE = whitespace
    SYMBOL = '()[]:*+-=;,<'
    COMMENT_SYMBOL = '/#'
    ALL = printable
    EOF = chr(3)
