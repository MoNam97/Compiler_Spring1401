# Danial Erfanian - 97110155
# Mohamad Namdar  - 97106302

from copy import copy
# Mohamadfrom parser import Parser
from anytree import RenderTree
from scanner import Scanner
from utils import KEYWORDS, TokenType


def write_tokens(recognized_tokens):
    with open("tokens.txt", "w+") as f:
        last_line = -1
        for lineno, token in recognized_tokens:
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

if __name__ == '__main__':
    recognized_tokens = []
    symbols = copy(KEYWORDS)
    scanner = Scanner("input.txt", symbols)
    lookahead = False
    
    parser = Parser("input.txt", symbols)
    parser.parse()
    
    for pre, fill, node in RenderTree(parser.parseTree):
        print("%s%s" % (pre, node.name))
    
    write_symbol_table(symbols)
    write_tokens(recognized_tokens)
    write_lexical_errors(scanner.lexical_errors)