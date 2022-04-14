class BaseLexicalError(BaseException):
    msg = ""

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"({self.text}, {self.msg})"


class InvalidInputError(BaseLexicalError):
    msg = "Invalid input"


class InvalidNumberError(BaseLexicalError):
    msg = "Invalid number"


class UnclosedCommentError(BaseLexicalError):
    msg = "Unclosed comment"


class UnmatchedCommentError(BaseLexicalError):
    msg = "Unmatched comment"
