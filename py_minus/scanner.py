from collections import namedtuple
from enum import Enum
from string import punctuation

from py_minus.lexical_errors import (
    BaseLexicalError,
    InvalidNumberError,
    InvalidInputError,
    UnmatchedCommentError,
    UnclosedCommentError
)
from py_minus.utils import TokenPack, TokenType, KEYWORDS, Char

# TODO:
# [x] Handle Invalid Inputs
# [x] next_state should consider sets
# [x] Remove last charracter hack
# [x] handle the INITIAL -> EOF token
# [x] error handling for errors starting with '/' + '*$' is NOT an Unmatched comment

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
    DIGIT_FINAL = StateItem(next(counter), TokenType.NUM, True)

    KEYWORD = StateItem(next(counter), False, False)
    KEYWORD_FINAL = StateItem(next(counter), TokenType.KEYWORD, True)

    WHITESPACE = StateItem(next(counter), False, False)
    WHITESPACE_FINAL = StateItem(next(counter), TokenType.WHITESPACE, True)

    COMMENT_ONELINE = StateItem(next(counter), False, False)
    COMMENT_MULTILINE1 = StateItem(next(counter), False, True)
    COMMENT_MULTILINE2 = StateItem(next(counter), False, True)
    COMMENT_MULTILINE3 = StateItem(next(counter), False, False)
    COMMENT_FINAL = StateItem(next(counter), TokenType.COMMENT, True)
    COMMENT_MULTILINE_FINAL = StateItem(next(counter), TokenType.COMMENT, False)

    END_OF_FILE = StateItem(next(counter), TokenType.EOF, False)


class DFA:
    initial_state = State.INITIAL
    next = [
        (State.INITIAL, Char.EOF, State.INITIAL),
        (State.INITIAL, '=', State.EQUAL_SYMBOL),
        (State.EQUAL_SYMBOL, '=', State.EQUAL_SYMBOL2),
        (State.EQUAL_SYMBOL, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL + Char.EOF,
         State.EQUAL_SYMBOL3),
        (State.INITIAL, '*', State.STAR),
        (State.STAR, '*', State.STAR2),
        (State.STAR, Char.LETTER + Char.DIGIT + Char.WHITESPACE + Char.SYMBOL + '#' + Char.EOF, State.STAR3),
        (State.INITIAL, Char.SYMBOL, State.SYMBOL_FINAL),

        # digit:
        (State.INITIAL, Char.DIGIT, State.DIGIT_INT),
        (State.DIGIT_INT, Char.DIGIT, State.DIGIT_INT),
        (State.DIGIT_INT, '.', State.DIGIT_FLOAT),
        (State.DIGIT_FLOAT, Char.DIGIT, State.DIGIT_FLOAT),
        (State.DIGIT_FLOAT, Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL + Char.EOF, State.DIGIT_FINAL),
        (State.DIGIT_INT, Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL + Char.EOF, State.DIGIT_FINAL),

        # Letter:
        (State.INITIAL, Char.LETTER, State.KEYWORD),
        (State.KEYWORD, Char.LETTER + Char.DIGIT, State.KEYWORD),
        (State.KEYWORD, Char.WHITESPACE + Char.SYMBOL + Char.COMMENT_SYMBOL + Char.EOF, State.KEYWORD_FINAL),

        # Whitespace:
        (State.INITIAL, Char.WHITESPACE, State.WHITESPACE),
        (State.WHITESPACE, Char.WHITESPACE, State.WHITESPACE),
        (State.WHITESPACE, Char.LETTER + Char.DIGIT + punctuation + Char.EOF, State.WHITESPACE_FINAL),

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
        (State.COMMENT_MULTILINE3, "*", State.COMMENT_MULTILINE3),
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
    symbols = None
    f = None
    last_lineno = 0
    lineno = 0
    last_char = None
    lexical_errors = []

    def __init__(self, filepath, symboltable):
        Scanner.reset(self)
        self.symbols = symboltable
        self.f = open(filepath, "r")

    @staticmethod
    def reset(self):
        self.current = DFA.initial_state  # INITIAL
        self.buffer = ""

    def eval_next_char(self, next_char):
        prev_state = self.current
        self.current = DFA.get_next_state(self.current, next_char)
        self.buffer = self.buffer + next_char
        if self.current is None:
            text = self.buffer
            Scanner.reset(self)
            return self.handle_panic_mode(prev_state, text)
        if self.current.value.token_type:  # State is final
            lookahead = self.current.value.lookahead
            if lookahead:
                self.buffer = self.buffer[:-1]
            result = TokenPack(-1, self.current.value.token_type, self.buffer)
            if result.token_type == TokenType.KEYWORD and self.buffer not in KEYWORDS:
                result = TokenPack(-1, TokenType.ID, self.buffer)
            Scanner.reset(self)
            return result, lookahead
        return None, False

    error_handler = {
        State.DIGIT_INT: InvalidNumberError,
        State.DIGIT_FLOAT: InvalidNumberError,
        State.KEYWORD: InvalidInputError,
        State.STAR: InvalidInputError,
        State.COMMENT_MULTILINE2: UnclosedCommentError,
        State.COMMENT_MULTILINE1: InvalidInputError,
        State.INITIAL: InvalidInputError
    }

    def handle_panic_mode(self, prev_state: State, text: str):
        if prev_state == State.STAR and text == "*/":
            Handler = UnmatchedCommentError
        else:
            Handler = self.error_handler.get(prev_state, InvalidInputError)
        if prev_state.value.lookahead:
            text = text[:-1]
        return Handler(text=text), prev_state.value.lookahead

    def get_next_token(self, lookahead: bool):
        while True:
            if not lookahead:
                next_char = self.f.read(1) or Char.EOF
                self.last_char = next_char
            else:
                next_char = self.last_char
            recognized_token, lookahead = self.eval_next_char(next_char)
            if isinstance(recognized_token, BaseLexicalError):
                self.lexical_errors.append((self.last_lineno, recognized_token))
                self.last_lineno = self.lineno
                continue
            elif recognized_token:
                recognized_token.lineno = self.last_lineno
                if recognized_token.token_type == TokenType.ID and recognized_token.lexim not in self.symbols:
                    self.symbols.append(recognized_token.lexim)
                self.last_lineno = self.lineno
                if recognized_token.token_type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                    return recognized_token, lookahead
                else:
                    continue
            if next_char == '\n':
                self.lineno += 1
            if next_char == Char.EOF:
                self.f.close()
                return TokenPack(self.last_lineno, TokenType.EOF, '$'), False
# Better to handle EOF in DFA
