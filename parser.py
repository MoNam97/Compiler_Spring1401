from collections import deque

from anytree import Node, RenderTree

from utils import TokenType, NonTerminal, KEYWORDS, EPSILON


# TODO:
# [x] if next_branch -> None
# [x] if next_branch -> -1
# [x] if next_branch -> something
# [x] implementation make_node method
# [x] Handle epsilon
# [x] Handle traling $
# [ ] Fix extra single qoutes in parse tree
# [ ] Consider non empty stack when EOF received

class Parser:
    scanner = None
    # current_token = None
    parseStack = deque()
    parseTree = Node("Program")
    parseTreeStack = [parseTree]
    syntaxError = []

    def __init__(self, scanner):
        self.scanner = scanner
        self.parseStack.extend([TokenType.EOF, NonTerminal.Program])

    def print_tree(self):
        for pre, fill, node in RenderTree(self.parseTree):
            print("%s%s" % (pre, node.name))

    def parse(self):
        lookahead = False
        token_pack, lookahead = self.scanner.get_next_token(lookahead)
        while True:
            self.print_tree()
            if isinstance(self.parseStack[-1], NonTerminal):
                self.derivate_non_terminal(token_pack)
            else:
                if not self.sameTerminal(token_pack[1]):
                    self.syntaxError.append((3, token_pack))
                    self.parseStack.pop()
                    self.parseTreeStack.pop()
                else:
                    self.parseStack.pop()
                    self.parseTreeStack.pop()
                    token_pack, lookahead = self.scanner.get_next_token(lookahead)

            if token_pack[1][0] == TokenType.EOF and len(self.parseStack) == 1:
                Node('$', parent=self.parseTree)
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

    def make_node(self, arg, token, parent):
        if isinstance(arg, NonTerminal):
            node = Node(arg.name, parent=parent)
        elif isinstance(arg, TokenType):
            node = Node((token[0].name, token[1]), parent=parent)
        elif arg in KEYWORDS:
            node = Node((TokenType.KEYWORD.name, arg), parent=parent)
        else:
            node = Node((TokenType.SYMBOL.name, arg), parent=parent)
        return node

    def sameTerminal(self, token_pack):
        token = token_pack[0]
        lexim = token_pack[1]
        if token in (TokenType.KEYWORD, TokenType.SYMBOL):
            return self.parseStack[-1] == lexim
        else:
            return self.parseStack[-1] == token

    def panic_mode(self, token_pack):
        if token_pack[1][0] == TokenType.EOF:
            self.syntaxError.append((4, token_pack))  # errorType , (lineno, token)
        else:
            self.syntaxError.append((1, token_pack))

    def derivate_non_terminal(self, token_pack):
        next_branch = self.next_move(token_pack[1])
        if next_branch is None:
            self.panic_mode(token_pack)
        elif next_branch == -1:
            self.syntaxError.append((2, token_pack))
            self.parseStack.pop()
            self.parseTreeStack.pop()
        else:
            parent = self.parseTreeStack[-1]
            self.parseTreeStack.pop()
            self.parseStack.pop()
            if next_branch == ():
                Node(EPSILON, parent=parent)
            nodes = []
            for arg in next_branch:
                nodes.append(self.make_node(arg, token_pack[1], parent))
            for arg, node in zip(next_branch[::-1], nodes[::-1]):
                self.parseStack.append(arg)
                self.parseTreeStack.append(node)


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

        (NonTerminal.Power, ';'): (NonTerminal.Primary,),
        (NonTerminal.Power, '['): (NonTerminal.Primary,),
        (NonTerminal.Power, ']'): (NonTerminal.Primary,),
        (NonTerminal.Power, '('): (NonTerminal.Primary,),
        (NonTerminal.Power, ')'): (NonTerminal.Primary,),
        (NonTerminal.Power, ','): (NonTerminal.Primary,),
        (NonTerminal.Power, ':'): (NonTerminal.Primary,),
        (NonTerminal.Power, '=='): (NonTerminal.Primary,),
        (NonTerminal.Power, '<'): (NonTerminal.Primary,),
        (NonTerminal.Power, '+'): (NonTerminal.Primary,),
        (NonTerminal.Power, '-'): (NonTerminal.Primary,),
        (NonTerminal.Power, '*'): (NonTerminal.Primary,),
        (NonTerminal.Power, '**'): ('**', NonTerminal.Factor),

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
