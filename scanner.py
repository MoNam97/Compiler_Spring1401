from collections import namedtuple
from enum import Enum
from string import punctuation

from lexical_errors import (
    InvalidNumberError,
    BaseLexicalError,
    InvalidInputError,
    UnmatchedCommentError,
    UnclosedCommentError
)
from utils import TokenType, IDENTIFIERS, Char

# TODO:
# [ ] Handle Invalid Inputs
# [x] next_state should consider sets
# [x] Remove last charracter hack

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

    WHITESPACE = StateItem(next(counter), False, False)
    WHITESPACE_FINAL = StateItem(next(counter), TokenType.WHITESPACE, True)
    # GARBAGE       = StateItem(5, True, False)

    COMMENT_ONELINE = StateItem(next(counter), False, False)
    COMMENT_MULTILINE1 = StateItem(next(counter), False, False)
    COMMENT_MULTILINE2 = StateItem(next(counter), False, False)
    COMMENT_MULTILINE3 = StateItem(next(counter), False, False)
    COMMENT_FINAL = StateItem(next(counter), TokenType.COMMENT, True)
    COMMENT_MULTILINE_FINAL = StateItem(next(counter), TokenType.COMMENT, False)


class DFA:
    initial_state = State.INITIAL
    next = [
        (State.INITIAL, '=', State.EQUAL_SYMBOL),
        (State.EQUAL_SYMBOL, '=', State.EQUAL_SYMBOL2),
        (State.EQUAL_SYMBOL, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL,
         State.EQUAL_SYMBOL3),
        (State.INITIAL, '*', State.STAR),
        (State.STAR, '*', State.STAR2),
        (State.STAR, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL + '#', State.STAR3),
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

        # Whitespace:
        (State.INITIAL, Char.WHITESPACE, State.WHITESPACE),
        (State.WHITESPACE, Char.WHITESPACE, State.WHITESPACE),
        (State.WHITESPACE, Char.LETTER + Char.DIGIT + punctuation, State.WHITESPACE_FINAL),

        # Comment:
        (State.INITIAL, '#', State.COMMENT_ONELINE),
        (State.COMMENT_ONELINE, Char.EOF + '\n', State.COMMENT_FINAL),
        (State.COMMENT_ONELINE, Char.ALL, State.COMMENT_ONELINE),

        # Comment multi line:
        (State.INITIAL, "/", State.COMMENT_MULTILINE1),
        (State.COMMENT_MULTILINE1, "*", State.COMMENT_MULTILINE2),
        (State.COMMENT_MULTILINE2, "*", State.COMMENT_MULTILINE3),
        (State.COMMENT_MULTILINE2, Char.ALL, State.COMMENT_MULTILINE2),
        (State.COMMENT_MULTILINE3, "/", State.COMMENT_MULTILINE_FINAL),
        (State.COMMENT_MULTILINE3, Char.ALL, State.COMMENT_MULTILINE2),
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
        prev_state = self.current
        self.current = DFA.get_next_state(self.current, next_char)
        self.buffer = self.buffer + next_char
        if self.current is None:
            text = self.buffer
            Scanner.reset(self)
            self.handle_panic_mode(prev_state, text)
        if self.current.value.token_type:  # State is final
            lookahead = self.current.value.lookahead
            if lookahead:
                self.buffer = self.buffer[:-1]
            result = (self.current.value.token_type, self.buffer)
            if result[0] == TokenType.KEYWORD and self.buffer not in IDENTIFIERS:
                result = (TokenType.ID, self.buffer)
            Scanner.reset(self)
            return result, lookahead
        return None, False

    error_handler = {
        State.DIGIT_INT: InvalidNumberError,
        State.DIGIT_FLOAT: InvalidNumberError,
        State.KEYWORD: InvalidInputError,
        State.STAR: UnmatchedCommentError,
        State.COMMENT_MULTILINE2: UnclosedCommentError,
        State.COMMENT_MULTILINE1: InvalidInputError,
        State.INITIAL: InvalidInputError
    }

    def handle_panic_mode(self, prev_state, text):
        print(text)
        Handler: BaseLexicalError = self.error_handler.get(prev_state, InvalidInputError)
        raise Handler(text=text)
