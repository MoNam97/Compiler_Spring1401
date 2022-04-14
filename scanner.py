from collections import namedtuple
from enum import Enum
from string import ascii_letters, digits, whitespace


# TODO:
# [ ] Handle Invalid Inputs
# [x] next_state should consider sets
# [ ] Remove last charracter hack

class TokenType(Enum):
    SYMBOL = 0


StateItem = namedtuple('State', ['id', 'accept', 'lookahead'])
counter = iter(range(1000000))


class State(Enum):
    INITIAL = StateItem(next(counter), False, False)
    ACC1 = StateItem(next(counter), True, False)
    EQUAL_SYMBOL = StateItem(next(counter), False, False)
    EQUAL_SYMBOL2 = StateItem(next(counter), True, False)
    EQUAL_SYMBOL3 = StateItem(next(counter), True, True)
    EQUAL_DIGIT_INT = StateItem(next(counter), False, False)
    EQUAL_DIGIT_FLOAT = StateItem(next(counter), False, False)
    EQUAL_DIGIT_FINAL = StateItem(next(counter), True, True)

    KEYWORD = StateItem(next(counter), False, False)
    KEYWORD_FINAL = StateItem(next(counter), True, True)
    # GARBAGE       = StateItem(5, True, False)


class Char:
    LETTER = ascii_letters
    DIGIT = digits
    WHITESPACE = whitespace
    SYMBOL = '()[]:*+-=;,<'


class DFA:
    initial_state = State.INITIAL
    next = [
        (State.INITIAL, '(', State.ACC1),
        (State.INITIAL, ')', State.ACC1),
        (State.INITIAL, '[', State.ACC1),
        (State.INITIAL, ']', State.ACC1),
        (State.INITIAL, ',', State.ACC1),
        (State.INITIAL, ':', State.ACC1),
        (State.INITIAL, '+', State.ACC1),
        (State.INITIAL, '-', State.ACC1),
        (State.INITIAL, '<', State.ACC1),
        (State.INITIAL, '=', State.EQUAL_SYMBOL),
        (State.EQUAL_SYMBOL, '=', State.EQUAL_SYMBOL2),
        (State.EQUAL_SYMBOL, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL, State.EQUAL_SYMBOL3),
        
        # digit:
        (State.INITIAL, Char.DIGIT, State.EQUAL_DIGIT_INT),
        (State.EQUAL_DIGIT_INT, Char.DIGIT, State.EQUAL_DIGIT_INT),
        (State.EQUAL_DIGIT_INT, '.', State.EQUAL_DIGIT_FLOAT),
        (State.EQUAL_DIGIT_FLOAT, Char.DIGIT, State.EQUAL_DIGIT_FLOAT),
        (State.EQUAL_DIGIT_FLOAT, Char.WHITESPACE + Char.SYMBOL, State.EQUAL_DIGIT_FINAL),
        (State.EQUAL_DIGIT_INT, Char.WHITESPACE + Char.SYMBOL, State.EQUAL_DIGIT_FINAL),

        # Letter:
        (State.INITIAL, Char.LETTER, State.KEYWORD),
        (State.KEYWORD, Char.LETTER + Char.DIGIT, State.KEYWORD),
        (State.KEYWORD, Char.WHITESPACE + Char.SYMBOL, State.KEYWORD_FINAL),
        # (state, character): state2,
    ]

    @staticmethod
    def get_next_state(current, next_char):
        for state, char_set, end_state in DFA.next:
            if state == current and next_char in char_set:
                return end_state


class Scanner:
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
        if self.current.value.accept:
            result = (TokenType.SYMBOL, self.buffer[-1])
            Scanner.reset(self)
            return result
