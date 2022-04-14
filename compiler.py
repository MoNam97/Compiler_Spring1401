# MN
# DE
from copy import copy

from scanner import Scanner
from utils import IDENTIFIERS, TokenType


def write_tokens(recognized_tokens):
    for lineno, token in recognized_tokens:
        print(f"{lineno}. ({token[0].name}, {token[1]})")


def write_symbol_table(symbols):
    with open("symbol_table.txt", "w+") as f:
        for idx, symbol in enumerate(symbols):
            f.write(f"{idx + 1}. {symbol}\n")


def run():
    scanner = Scanner()
    recognized_tokens = []
    symbols = copy(IDENTIFIERS)
    with open("PA1-Testcases/T01/input.txt", "r") as f:
        lineno = 0
        while next_char := f.read(1):
            if next_char == '\n':
                lineno += 1
            lookahead = True
            while lookahead:
                recognized_token, lookahead = scanner.get_next_token(next_char)
                if recognized_token:
                    recognized_tokens.append((lineno + 1, recognized_token))
                    if recognized_token[0] == TokenType.ID and recognized_token[1] not in symbols:
                        symbols.append(recognized_token[1])
    write_symbol_table(symbols)
    write_tokens(recognized_tokens)


if __name__ == '__main__':
    run()
