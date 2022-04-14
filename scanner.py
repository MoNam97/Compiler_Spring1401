from collections import namedtuple
from enum import Enum

StateItem = namedtuple('State', ['id', 'accept', 'lookahead'])


class TokenType(Enum):
    SYMBOL = 0


class State(Enum):
    INITIAL = StateItem(0, False, False)
    ACC = StateItem(1, True, False)


class DFA:
    initial_state = State.INITIAL
    next = {
        (State.INITIAL, '('): State.ACC,
        (State.INITIAL, ')'): State.ACC,
        # (state, character): state2,
    }

    @staticmethod
    def get_next_state(current, next_char):
        return DFA.next.get((current, next_char)) or State.INITIAL


class Scanner:
    def __init__(self):
        self.current = DFA.initial_state  # INITIAL
        self.buffer = ""

    def get_next_token(self, next_char):
        self.current = DFA.get_next_state(self.current, next_char)
        self.buffer = self.buffer + next_char
        if self.current.value.accept:
            result = (TokenType.SYMBOL, self.buffer[-1])
            self.buffer = ""
            self.current = DFA.initial_state
            return result
