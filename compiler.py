# Danial Erfanian - 97110155
# Mohamad Namdar  - 97106302

from copy import copy

from anytree import RenderTree

from py_minus.code_gen import CodeGenerator
from py_minus.parser import Parser
from py_minus.scanner import Scanner
from py_minus.utils import KEYWORDS, TokenType


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


def write_syntax_errors(errors):
    with open("syntax_errors.txt", "w+") as f:
        if len(errors) == 0:
            f.write("There is no syntax error.")
        for error in errors:
            f.write(f"#{error[1].lineno + 1} : ")
            if error[0] == 3:
                f.write(f"syntax error, missing {error[-1]}\n")
            elif error[0] == 1:
                if error[1].token_type in [TokenType.SYMBOL, TokenType.KEYWORD]:
                    arg = error[1].lexim
                else:
                    arg = error[1].token_type.name
                f.write(f"syntax error, illegal {arg}\n")
            elif error[0] == 2:
                f.write(f"syntax error, missing {error[-1].name}\n")
                # TODO: on line chi shod?
            elif error[0] == 4:
                f.write(f"syntax error, Unexpected EOF")
            else:
                assert False


def write_parse_tree(tree):
    with open("parse_tree.txt", "w+") as f:
        for pre, fill, node in RenderTree(tree):
            f.write("%s%s\n" % (pre, node.name))


def write_ouptut(gen):
    with open("output.txt", "w+") as f:
        gen.print(f)


if __name__ == '__main__':
    recognized_tokens = []
    symbols = copy(KEYWORDS)
    scanner = Scanner("input.txt", symbols)
    code_gen = CodeGenerator()

    parser = Parser(scanner, code_gen)
    parser.parse()

    # parser.print_tree()

    # print(parser.syntaxError)

    code_gen.print()

    write_ouptut(code_gen)
    write_parse_tree(parser.parseTree)
    write_syntax_errors(parser.syntaxError)
    write_symbol_table(symbols)
    write_tokens(recognized_tokens)
    write_lexical_errors(scanner.lexical_errors)
