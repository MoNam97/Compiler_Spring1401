# MN
# DE
from scanner import Scanner


def run():
    scanner = Scanner()
    with open("PA1-Testcases/T01/input.txt", "r") as f:
        while next_char := f.read(1):
            recognized_token = scanner.get_next_token(next_char)
            if recognized_token:
                print(recognized_token)


if __name__ == '__main__':
    run()
