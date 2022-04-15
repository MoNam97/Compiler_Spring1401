# Danial Erfanian - 97110155
# Mohamad Namdar  - 97106302
import itertools
from copy import copy

from lexical_errors import BaseLexicalError
from scanner import Scanner
from utils import IDENTIFIERS, TokenType, Char


def write_tokens(recognized_tokens):
    with open("tokens.txt", "w+") as f:
        last_line = -1
        for lineno, token in recognized_tokens:
            if token[0] not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                if last_line < lineno:
                    if last_line != -1:
                        f.write('\n')
                    f.write(f"{lineno + 1}. ")
                    last_line = lineno
                f.write(f"({token[0].name}, {token[1]}) ")


def write_symbol_table(symbols):
    with open("symbol_table.txt", "w+") as f:
        for idx, symbol in enumerate(symbols):
            f.write(f"{idx + 1}. {symbol}\n")


def write_lexical_errors(lexical_errors):
    with open("lexical_errors.txt", "w+") as f:
        first_line = True
        last_line = -1
        if len(lexical_errors) == 0:
            f.write('There is no lexical error.')
        for lineno, error in lexical_errors:
            if last_line < lineno:
                if not first_line:
                    f.write('\n')
                first_line = False
                f.write(f"{lineno + 1}.")
                last_line = lineno
            f.write(f" {error}")


def run():
    scanner = Scanner()
    recognized_tokens = []
    symbols = copy(IDENTIFIERS)
    lexical_errors = []
    with open("input.txt", "r") as f:
        last_lineno = 0
        lineno = 0
        while True:
            next_char = f.read(1) or Char.EOF
            lookahead = True
            try:
                while lookahead:
                    recognized_token, lookahead = scanner.get_next_token(next_char)
                    if recognized_token:
                        recognized_tokens.append((last_lineno, recognized_token))
                        if recognized_token[0] == TokenType.ID and recognized_token[1] not in symbols:
                            symbols.append(recognized_token[1])
                        last_lineno = lineno
            except BaseLexicalError as e:
                lexical_errors.append((last_lineno, e))
                last_lineno = lineno
            if next_char == '\n':
                lineno += 1
            if next_char == Char.EOF:
                break

    write_symbol_table(symbols)
    write_tokens(recognized_tokens)
    write_lexical_errors(lexical_errors)


if __name__ == '__main__':
    run()
