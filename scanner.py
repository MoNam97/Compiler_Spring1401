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


class State(Enum):
    INITIAL = StateItem(0, False, False)
    ACC1 = StateItem(1, True, False)
    EQUAL_SYMBOL = StateItem(2, False, False)
    EQUAL_SYMBOL2 = StateItem(3, True, False)
    EQUAL_SYMBOL3 = StateItem(4, True, True)
    EQUAL_DIGIT_INT = StateItem(5, False, False)
    EQUAL_DIGIT_FLOAT = StateItem(6, False, False)
    EQUAL_DIGIT_FINAL = StateItem(7, True, True)
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
        (State.INITIAL, Char.DIGIT, State.EQUAL_DIGIT_INT),
        (State.EQUAL_SYMBOL, '=', State.EQUAL_SYMBOL2),
        (State.EQUAL_SYMBOL, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL, State.EQUAL_SYMBOL3),
        (State.EQUAL_DIGIT_INT, Char.DIGIT, State.EQUAL_DIGIT_INT),
        (State.EQUAL_DIGIT_INT, '.', State.EQUAL_DIGIT_FLOAT),
        (State.EQUAL_DIGIT_FLOAT, Char.DIGIT, State.EQUAL_DIGIT_FLOAT),
        (State.EQUAL_DIGIT_FLOAT, Char.WHITESPACE + Char.SYMBOL, State.EQUAL_DIGIT_FINAL),
        (State.EQUAL_DIGIT_INT, Char.WHITESPACE + Char.SYMBOL, State.EQUAL_DIGIT_FINAL),
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
