# Danial Erfanian - 97110155
# Mohamad Namdar  - 97106302

from copy import copy

from lexical_errors import BaseLexicalError
from scanner import Scanner
from utils import IDENTIFIERS, TokenType, Char


def write_tokens(recognized_tokens):
    with open("tokens.txt", "w+") as f:
        last_line = -1
        for lineno, token in recognized_tokens:
            if token[0] != TokenType.WHITESPACE:
                if last_line < lineno:
                    if lineno != 0:
                        f.write('\n')
                    f.write(f"{lineno + 1}. ")
                    last_line = lineno
                f.write(f"({token[0].name}, {token[1]}) ")


def write_symbol_table(symbols):
    with open("symbol_table.txt", "w+") as f:
        for idx, symbol in enumerate(symbols):
            f.write(f"{idx + 1}. {symbol}\n")


def write_lexical_errors(lexical_errors):
    print(lexical_errors)

# "PA1-Testcases/T01/input.txt"
def run():
    scanner = Scanner()
    recognized_tokens = []
    symbols = copy(IDENTIFIERS)
    lexical_errors = []
    with open("input.txt", "r") as f:
        lineno = 0
        while True:
            next_char = f.read(1) or Char.EOF
            lookahead = True
            try:
                while lookahead:
                    recognized_token, lookahead = scanner.get_next_token(next_char)
                    if recognized_token:
                        recognized_tokens.append((lineno, recognized_token))
                        if recognized_token[0] == TokenType.ID and recognized_token[1] not in symbols:
                            symbols.append(recognized_token[1])
            except BaseLexicalError as e:
                lexical_errors.append((lineno, e))
            if next_char == '\n':
                lineno += 1
            if next_char == Char.EOF:
                break

    write_symbol_table(symbols)
    write_tokens(recognized_tokens)
    write_lexical_errors(lexical_errors)


if __name__ == '__main__':
    run()
