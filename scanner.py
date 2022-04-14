from collections import namedtuple
from enum import Enum
from gc import garbage
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
    #GARBAGE       = StateItem(5, True, False)


class Char(Enum):
    LETTER = set(ascii_letters)
    DIGIT = set(digits)
    WHITESPACE = set(whitespace)
    SYMBOL = set('()[]:*+-=;,<')


class DFA:
    initial_state = State.INITIAL
    next = [
        ((State.INITIAL, '('), State.ACC1),
        ((State.INITIAL, ')'), State.ACC1),
        ((State.INITIAL, '['), State.ACC1),
        ((State.INITIAL, ']'), State.ACC1),
        ((State.INITIAL, ','), State.ACC1),
        ((State.INITIAL, ':'), State.ACC1),
        ((State.INITIAL, '+'), State.ACC1),
        ((State.INITIAL, '-'), State.ACC1),
        ((State.INITIAL, '<'), State.ACC1),
        ((State.INITIAL, '='), State.EQUAL_SYMBOL),
        ((State.EQUAL_SYMBOL, '='), State.EQUAL_SYMBOL2),
        ((State.EQUAL_SYMBOL, {Char.LETTER, Char.DIGIT, Char.WHITESPACE, Char.SYMBOL}), State.EQUAL_SYMBOL3)
        # (state, character): state2,
    ]

    @staticmethod
    def get_next_state(current, next_char):
        for key, end_state in DFA.next:
            (state, char_set) = key
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
        if self.current == None:
            print(self.buffer)
            Scanner.reset(self)
        if self.current.value.accept:
            result = (TokenType.SYMBOL, self.buffer[-1])
            Scanner.reset(self)
            return result
    
        

