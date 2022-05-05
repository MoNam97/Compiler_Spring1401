from collections import deque

from anytree import Node

from scanner import Scanner
from utils import TokenType, NonTerminal


# TODO:
# [x] if next_branch -> None
# [x] if next_branch -> -1
# [x] if next_branch -> something
# [x] implementation make_node method

class Parser:
    scanner = None
    # current_token = None
    parseStack = deque()
    parseTree = Node("Program")
    syntaxError = []

    def __init__(self, filepath, symbol):
        self.scanner = Scanner(filepath, symbol)
        self.parseStack.extend([TokenType.EOF, NonTerminal.Program])

    def parse(self):
        lookahead = False
        token_pack, lookahead = self.scanner.get_next_token(lookahead)
        while True:
            if isinstance(self.parseStack[-1], NonTerminal):
                next_branch = self.next_move(token_pack[1])
                print(next_branch)
                if next_branch is None:
                    if token_pack[1][0] == TokenType.EOF:
                        self.syntaxError.append((4, token_pack))  # errorType , (lineno, token)
                    else:
                        self.syntaxError.append((1, token_pack))
                        continue
                elif next_branch == -1:
                    self.syntaxError.append((2, token_pack))
                    self.parseStack.pop()
                else:
                    print(next_branch)
                    for arg in next_branch:
                        self.make_node(arg, token_pack[1])
                    for arg in next_branch[::-1]:
                        self.parseStack.append(arg)
            else:
                if not self.sameTerminal(token_pack[1]):
                    self.syntaxError.append((3, token_pack))
                    self.parseStack.pop()
                else:
                    self.parseStack.pop()
                    token_pack, lookahead = self.scanner.get_next_token(lookahead)

            if token_pack[1][0] == TokenType.EOF:
                break

    def next_move(self, token_pack):
        token = token_pack[0]
        lexim = token_pack[1]
        if token in (TokenType.KEYWORD, TokenType.SYMBOL):
            if (self.parseStack[-1], lexim) in ParseTable.next:
                return ParseTable.next[(self.parseStack[-1], lexim)]
        else:
            if (self.parseStack[-1], token) in ParseTable.next:
                return ParseTable.next[(self.parseStack[-1], token)]
        return None

    def make_node(self, arg, token):
        if isinstance(arg, NonTerminal):
            node = Node(arg.name, parent=self.parseStack[-1])
        else:
            if isinstance(arg, TokenType):
                node = Node((token[0].name, token[1]), parent=self.parseStack[-1])

    def sameTerminal(self, token_pack):
        token = token_pack[0]
        lexim = token_pack[1]
        if token in (TokenType.KEYWORD, TokenType.SYMBOL):
            return self.parseStack[-1] == lexim
        else:
            return self.parseStack[-1] == token

    def nameof(self, arg):
        if arg == NonTerminal.Program:
            name = 'Program'
        elif arg == NonTerminal.Statements:
            name = 'Statements'
        elif arg == NonTerminal.Statement:
            name = 'Statement'
        elif arg == NonTerminal.Simple_stmt:
            name = 'Simple_stmt'
        elif arg == NonTerminal.Compound_stmt:
            name = 'Compound_stmt'
        elif arg == NonTerminal.Assignment_Call:
            name = 'Assignment_Call'
        elif arg == NonTerminal.B:
            name = 'B'
        elif arg == NonTerminal.C:
            name = 'C'
        elif arg == NonTerminal.List_Rest:
            name = 'List_Rest'
        elif arg == NonTerminal.Return_stmt:
            name = 'Return_stmt'
        elif arg == NonTerminal.Return_Value:
            name = 'Return_Value'
        elif arg == NonTerminal.Global_stmt:
            name = 'Global_stmt'
        elif arg == NonTerminal.Function_def:
            name = 'Function_def'
        elif arg == NonTerminal.Params:
            name = 'Params'
        elif arg == NonTerminal.Params_Prime:
            name = 'Params_Prime'
        elif arg == NonTerminal.If_stmt:
            name = 'If_stmt'
        elif arg == NonTerminal.Else_block:
            name = 'Else_block'
        elif arg == NonTerminal.Iteration_stmt:
            name = 'Iteration_stmt'
        elif arg == NonTerminal.Relational_Expression:
            name = 'Relational_Expression'
        elif arg == NonTerminal.Relop:
            name = 'Relop'
        elif arg == NonTerminal.Expression:
            name = 'Expression'
        elif arg == NonTerminal.Expression_Prime:
            name = 'Expression_Prime'
        elif arg == NonTerminal.Term:
            name = 'Term'
        elif arg == NonTerminal.Term_Prime:
            name = 'Term_Prime'
        elif arg == NonTerminal.Factor:
            name = 'Factor'
        elif arg == NonTerminal.Power:
            name = 'Power'
        elif arg == NonTerminal.Primary:
            name = 'Primary'
        elif arg == NonTerminal.Arguments:
            name = 'Arguments'
        elif arg == NonTerminal.Arguments_Prime:
            name = 'Arguments_Prime'
        elif arg == NonTerminal.Atom:
            name = 'Atom'
        return name


class ParseTable:
    next = {
        (NonTerminal.Program, 'break'): (NonTerminal.Statements,),
        (NonTerminal.Program, 'continue'): (NonTerminal.Statements,),
        (NonTerminal.Program, TokenType.ID): (NonTerminal.Statements,),
        (NonTerminal.Program, 'return'): (NonTerminal.Statements,),
        (NonTerminal.Program, 'global'): (NonTerminal.Statements,),
        (NonTerminal.Program, 'def'): (NonTerminal.Statements,),
        (NonTerminal.Program, 'if'): (NonTerminal.Statements,),
        (NonTerminal.Program, 'while'): (NonTerminal.Statements,),
        (NonTerminal.Program, TokenType.EOF): (NonTerminal.Statements,),

        (NonTerminal.Statements, ';'): (),
        (NonTerminal.Statements, 'else'): (),
        (NonTerminal.Statements, TokenType.EOF): (),
        (NonTerminal.Statements, 'break'): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'continue'): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, TokenType.ID): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'return'): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'global'): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'def'): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'if'): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'while'): (NonTerminal.Statement, ';', NonTerminal.Statements),

        (NonTerminal.Statement, ';'): -1,
        (NonTerminal.Statement, 'break'): (NonTerminal.Simple_stmt,),
        (NonTerminal.Statement, 'continue'): (NonTerminal.Simple_stmt,),
        (NonTerminal.Statement, TokenType.ID): (NonTerminal.Simple_stmt,),
        (NonTerminal.Statement, 'return'): (NonTerminal.Simple_stmt,),
        (NonTerminal.Statement, 'global'): (NonTerminal.Simple_stmt,),
        (NonTerminal.Statement, 'def'): (NonTerminal.Compound_stmt,),
        (NonTerminal.Statement, 'if'): (NonTerminal.Compound_stmt,),
        (NonTerminal.Statement, 'while'): (NonTerminal.Compound_stmt,),

        (NonTerminal.Simple_stmt, ';'): -1,
        (NonTerminal.Simple_stmt, 'break'): ('break',),
        (NonTerminal.Simple_stmt, 'continue'): ('continue',),
        (NonTerminal.Simple_stmt, TokenType.ID): (NonTerminal.Assignment_Call,),
        (NonTerminal.Simple_stmt, 'return'): (NonTerminal.Return_stmt,),
        (NonTerminal.Simple_stmt, 'global'): (NonTerminal.Global_stmt,),

        (NonTerminal.Compound_stmt, ';'): -1,
        (NonTerminal.Compound_stmt, 'def'): (NonTerminal.Function_def,),
        (NonTerminal.Compound_stmt, 'if'): (NonTerminal.If_stmt,),
        (NonTerminal.Compound_stmt, 'while'): (NonTerminal.Iteration_stmt,),

        (NonTerminal.Assignment_Call, ';'): -1,
        (NonTerminal.Assignment_Call, TokenType.ID): (TokenType.ID, NonTerminal.B),

        (NonTerminal.B, ';'): -1,
        (NonTerminal.B, '='): ('=', NonTerminal.C),
        (NonTerminal.B, '['): ('[', NonTerminal.Expression, ']', '=', NonTerminal.C),
        (NonTerminal.B, '('): ('(', NonTerminal.Arguments, ')'),

        (NonTerminal.C, ';'): -1,
        (NonTerminal.C, TokenType.ID): (NonTerminal.Expression,),
        (NonTerminal.C, TokenType.NUMBER): (NonTerminal.Expression,),
        (NonTerminal.C, '['): ('[', NonTerminal.Expression, NonTerminal.List_Rest, ']'),

        (NonTerminal.List_Rest, ']'): (),
        (NonTerminal.List_Rest, ','): (',', NonTerminal.Expression, NonTerminal.List_Rest),

        (NonTerminal.Return_stmt, ';'): -1,
        (NonTerminal.Return_stmt, 'return'): ('return', NonTerminal.Return_Value),
        (NonTerminal.Return_Value, ';'): (),
        (NonTerminal.Return_Value, TokenType.ID): (NonTerminal.Expression,),
        (NonTerminal.Return_Value, TokenType.NUMBER): (NonTerminal.Expression,),

        (NonTerminal.Global_stmt, ';'): -1,
        (NonTerminal.Global_stmt, 'global'): ('global', TokenType.ID),

        (NonTerminal.Function_def, ';'): -1,
        (NonTerminal.Function_def, 'def'): (
            'def', TokenType.ID, '(', NonTerminal.Params, ')', ':', NonTerminal.Statements),

        (NonTerminal.Params, ')'): (),
        (NonTerminal.Params, TokenType.ID): (TokenType.ID, NonTerminal.Params_Prime),
        (NonTerminal.Params_Prime, ')'): (),
        (NonTerminal.Params_Prime, ','): (',', TokenType.ID, NonTerminal.Params_Prime),

        # if else while blocks
        (NonTerminal.If_stmt, ';'): -1,
        (NonTerminal.Iteration_stmt, ';'): -1,
        (NonTerminal.Else_block, ';'): (),
        (NonTerminal.If_stmt, 'if'): (
            'if', NonTerminal.Relational_Expression, ':', NonTerminal.Statements, NonTerminal.Else_block),
        (NonTerminal.Else_block, 'else'): ('else', ':', NonTerminal.Statements),
        (NonTerminal.Iteration_stmt, 'while'): (
            'while', '(', NonTerminal.Relational_Expression, ')', NonTerminal.Statements),

        (NonTerminal.Relational_Expression, ')'): -1,
        (NonTerminal.Relational_Expression, ':'): -1,
        (NonTerminal.Relational_Expression, TokenType.ID): (
            NonTerminal.Expression, NonTerminal.Relop, NonTerminal.Expression),
        (NonTerminal.Relational_Expression, TokenType.NUMBER): (
            NonTerminal.Expression, NonTerminal.Relop, NonTerminal.Expression),

        (NonTerminal.Relop, TokenType.ID): -1,
        (NonTerminal.Relop, TokenType.NUMBER): -1,
        (NonTerminal.Relop, '=='): ('==',),
        (NonTerminal.Relop, '<'): ('<',),

        (NonTerminal.Expression, ';'): -1,
        (NonTerminal.Expression, ']'): -1,
        (NonTerminal.Expression, ')'): -1,
        (NonTerminal.Expression, ','): -1,
        (NonTerminal.Expression, ':'): -1,
        (NonTerminal.Expression, '=='): -1,
        (NonTerminal.Expression, '<'): -1,
        (NonTerminal.Expression, TokenType.ID): (NonTerminal.Term, NonTerminal.Expression_Prime),
        (NonTerminal.Expression, TokenType.NUMBER): (NonTerminal.Term, NonTerminal.Expression_Prime),

        (NonTerminal.Expression_Prime, ';'): (),
        (NonTerminal.Expression_Prime, ']'): (),
        (NonTerminal.Expression_Prime, ')'): (),
        (NonTerminal.Expression_Prime, ','): (),
        (NonTerminal.Expression_Prime, ':'): (),
        (NonTerminal.Expression_Prime, '=='): (),
        (NonTerminal.Expression_Prime, '<'): (),
        (NonTerminal.Expression_Prime, '+'): ('+', NonTerminal.Term, NonTerminal.Expression_Prime),
        (NonTerminal.Expression_Prime, '-'): ('+', NonTerminal.Term, NonTerminal.Expression_Prime),

        (NonTerminal.Term, ';'): -1,
        (NonTerminal.Term, ']'): -1,
        (NonTerminal.Term, ')'): -1,
        (NonTerminal.Term, ','): -1,
        (NonTerminal.Term, ':'): -1,
        (NonTerminal.Term, '=='): -1,
        (NonTerminal.Term, '<'): -1,
        (NonTerminal.Term, '+'): -1,
        (NonTerminal.Term, '-'): -1,
        (NonTerminal.Term, TokenType.ID): (NonTerminal.Factor, NonTerminal.Term_Prime),
        (NonTerminal.Term, TokenType.NUMBER): (NonTerminal.Factor, NonTerminal.Term_Prime),

        (NonTerminal.Term_Prime, ';'): (),
        (NonTerminal.Term_Prime, ']'): (),
        (NonTerminal.Term_Prime, ')'): (),
        (NonTerminal.Term_Prime, ','): (),
        (NonTerminal.Term_Prime, ':'): (),
        (NonTerminal.Term_Prime, '=='): (),
        (NonTerminal.Term_Prime, '<'): (),
        (NonTerminal.Term_Prime, '+'): (),
        (NonTerminal.Term_Prime, '-'): (),
        (NonTerminal.Term_Prime, '*'): ('*', NonTerminal.Factor, NonTerminal.Term_Prime),

        (NonTerminal.Factor, ';'): -1,
        (NonTerminal.Factor, ']'): -1,
        (NonTerminal.Factor, ')'): -1,
        (NonTerminal.Factor, ','): -1,
        (NonTerminal.Factor, ':'): -1,
        (NonTerminal.Factor, '=='): -1,
        (NonTerminal.Factor, '<'): -1,
        (NonTerminal.Factor, '+'): -1,
        (NonTerminal.Factor, '-'): -1,
        (NonTerminal.Factor, '*'): -1,
        (NonTerminal.Factor, TokenType.ID): (NonTerminal.Atom, NonTerminal.Power),
        (NonTerminal.Factor, TokenType.NUMBER): (NonTerminal.Atom, NonTerminal.Power),

        (NonTerminal.Factor, ';'): (NonTerminal.Primary,),
        (NonTerminal.Factor, '['): (NonTerminal.Primary,),
        (NonTerminal.Factor, ']'): (NonTerminal.Primary,),
        (NonTerminal.Factor, '('): (NonTerminal.Primary,),
        (NonTerminal.Factor, ')'): (NonTerminal.Primary,),
        (NonTerminal.Factor, ','): (NonTerminal.Primary,),
        (NonTerminal.Factor, ':'): (NonTerminal.Primary,),
        (NonTerminal.Factor, '=='): (NonTerminal.Primary,),
        (NonTerminal.Factor, '<'): (NonTerminal.Primary,),
        (NonTerminal.Factor, '+'): (NonTerminal.Primary,),
        (NonTerminal.Factor, '-'): (NonTerminal.Primary,),
        (NonTerminal.Factor, '*'): (NonTerminal.Primary,),
        (NonTerminal.Factor, '**'): ('**', NonTerminal.Factor),

        (NonTerminal.Primary, ';'): (),
        (NonTerminal.Primary, '['): ('[', NonTerminal.Expression, ']', NonTerminal.Primary),
        (NonTerminal.Primary, ']'): (),
        (NonTerminal.Primary, '('): ('(', NonTerminal.Arguments, ')', NonTerminal.Primary),
        (NonTerminal.Primary, ')'): (),
        (NonTerminal.Primary, ','): (),
        (NonTerminal.Primary, ':'): (),
        (NonTerminal.Primary, '=='): (),
        (NonTerminal.Primary, '<'): (),
        (NonTerminal.Primary, '+'): (),
        (NonTerminal.Primary, '-'): (),
        (NonTerminal.Primary, '*'): (),

        (NonTerminal.Arguments, ')'): (),
        (NonTerminal.Arguments, TokenType.ID): (NonTerminal.Expression, NonTerminal.Arguments_Prime),
        (NonTerminal.Arguments, TokenType.NUMBER): (NonTerminal.Expression, NonTerminal.Arguments_Prime),

        (NonTerminal.Arguments_Prime, ')'): (),
        (NonTerminal.Arguments_Prime, ','): (',', NonTerminal.Expression, NonTerminal.Arguments_Prime),

        (NonTerminal.Atom, ';'): -1,
        (NonTerminal.Atom, '['): -1,
        (NonTerminal.Atom, ']'): -1,
        (NonTerminal.Atom, '('): -1,
        (NonTerminal.Atom, ')'): -1,
        (NonTerminal.Atom, ','): -1,
        (NonTerminal.Atom, ':'): -1,
        (NonTerminal.Atom, '=='): -1,
        (NonTerminal.Atom, '<'): -1,
        (NonTerminal.Atom, '+'): -1,
        (NonTerminal.Atom, '-'): -1,
        (NonTerminal.Atom, '*'): -1,
        (NonTerminal.Atom, '**'): -1,
        (NonTerminal.Atom, TokenType.ID): (TokenType.ID,),
        (NonTerminal.Atom, TokenType.NUMBER): (TokenType.NUMBER,)
    }
