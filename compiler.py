# MN
# DE
from scanner import Scanner


def initialize_symboltable():
    return ['break', 'continue', 'def', 'else', 'if', 'return', 'while']


def write_tokens(recognized_tokens):
    for lineno, token in recognized_tokens:
        print(f"{lineno}. ({token[0].name}, {token[1]})")


def run():
    scanner = Scanner()
    recognized_tokens = []
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

    write_tokens(recognized_tokens)


if __name__ == '__main__':
    symboltable = initialize_symboltable()
    run()
