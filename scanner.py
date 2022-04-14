from collections import namedtuple
from enum import Enum
from string import ascii_letters, digits, whitespace

from utils import TokenType, IDENTIFIERS

# TODO:
# [ ] Handle Invalid Inputs
# [x] next_state should consider sets
# [ ] Remove last charracter hack

StateItem = namedtuple('State', ['id', 'token_type', 'lookahead'])
counter = iter(range(1000000))


class State(Enum):
    INITIAL = StateItem(next(counter), False, False)
    SYMBOL_FINAL = StateItem(next(counter), TokenType.SYMBOL, False)
    EQUAL_SYMBOL = StateItem(next(counter), False, False)
    EQUAL_SYMBOL2 = StateItem(next(counter), TokenType.SYMBOL, False)
    EQUAL_SYMBOL3 = StateItem(next(counter), TokenType.SYMBOL, True)
    STAR = StateItem(next(counter), False, False)
    STAR2 = StateItem(next(counter), TokenType.SYMBOL, False)
    STAR3 = StateItem(next(counter), TokenType.SYMBOL, True)

    DIGIT_INT = StateItem(next(counter), False, False)
    DIGIT_FLOAT = StateItem(next(counter), False, False)
    DIGIT_FINAL = StateItem(next(counter), TokenType.NUMBER, True)

    KEYWORD = StateItem(next(counter), False, False)
    KEYWORD_FINAL = StateItem(next(counter), TokenType.KEYWORD, True)
    # GARBAGE       = StateItem(5, True, False)


class Char:
    LETTER = ascii_letters
    DIGIT = digits
    WHITESPACE = whitespace
    SYMBOL = '()[]:*+-=;,<'
    COMMENT_SYMBOL = '/#'


class DFA:
    initial_state = State.INITIAL
    next = [
        (State.INITIAL, '=', State.EQUAL_SYMBOL),
        (State.EQUAL_SYMBOL, '=', State.EQUAL_SYMBOL2),
        (State.EQUAL_SYMBOL, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL,
         State.EQUAL_SYMBOL3),
        (State.INITIAL, '*', State.STAR),
        (State.STAR, '*', State.STAR2),
        (State.STAR, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL, State.STAR3),
        (State.INITIAL, Char.SYMBOL, State.SYMBOL_FINAL),

        # digit:
        (State.INITIAL, Char.DIGIT, State.DIGIT_INT),
        (State.DIGIT_INT, Char.DIGIT, State.DIGIT_INT),
        (State.DIGIT_INT, '.', State.DIGIT_FLOAT),
        (State.DIGIT_FLOAT, Char.DIGIT, State.DIGIT_FLOAT),
        (State.DIGIT_FLOAT, Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL, State.DIGIT_FINAL),
        (State.DIGIT_INT, Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL, State.DIGIT_FINAL),

        # Letter:
        (State.INITIAL, Char.LETTER, State.KEYWORD),
        (State.KEYWORD, Char.LETTER + Char.DIGIT, State.KEYWORD),
        (State.KEYWORD, Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL, State.KEYWORD_FINAL),
        # (state, character): state2,
    ]

    @staticmethod
    def get_next_state(current, next_char):
        for state, char_set, end_state in DFA.next:
            if state == current and next_char in char_set:
                return end_state


class Scanner:
    current = None
    buffer = None

    def __init__(self):
        Scanner.reset(self)

    @staticmethod
    def reset(self):
        self.current = DFA.initial_state  # INITIAL
        self.buffer = ""

    def get_next_token(self, next_char):
        self.current = DFA.get_next_state(self.current, next_char)
        self.buffer = self.buffer + next_char
        if self.current is None:
            print(self.buffer)
            Scanner.reset(self)
        if self.current.value.token_type:  # State is final
            if self.current.value.lookahead:
                self.buffer = self.buffer[:-1]
            result = (self.current.value.token_type, self.buffer)
            if result[0] == TokenType.KEYWORD and self.buffer not in IDENTIFIERS:
                result = (TokenType.ID, self.buffer)
            Scanner.reset(self)
            return result, self.current.value.lookahead
        return None, False
