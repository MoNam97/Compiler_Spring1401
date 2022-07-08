from collections import deque

from anytree import Node, RenderTree

from py_minus.code_gen import CodeGenerator
from py_minus.scanner import Scanner
from py_minus.utils import TokenPack, TokenType, NonTerminal, KEYWORDS, EPSILON, ActionSymbols


# TODO:
# [x] if next_branch -> None
# [x] if next_branch -> -1
# [x] if next_branch -> something
# [x] implementation make_node method
# [x] Handle epsilon
# [x] Handle traling $
# [x] Fix extra single qoutes in parse tree
# [x] Consider non empty stack when EOF received
# [x] Write to files

class Parser:
    scanner = None
    # current_token = None
    parseStack = deque()
    parseTree = Node("Program")
    parseTreeStack = [parseTree]
    syntaxError = []
    lookahead = False
    current_token = None

    def __init__(self, scanner: Scanner, code_gen: CodeGenerator):
        self.scanner = scanner
        self.code_gen = code_gen
        self.parseStack.extend([TokenType.EOF, NonTerminal.Program])

    def print_tree(self):
        for pre, fill, node in RenderTree(self.parseTree):
            print("%s%s" % (pre, node.name))

    def parse(self):
        self.go_next_token()
        while True:
            # self.print_tree()
            if isinstance(self.parseStack[-1], NonTerminal):
                self.derivate_non_terminal(self.current_token)
            elif isinstance(self.parseStack[-1], ActionSymbols):
                arg = self.parseStack[-1]
                self.parseStack.pop()
                self.parseTreeStack.pop()
                self.code_gen.handle(arg, self.current_token)
            else:
                if not self.same_terminal(self.current_token):
                    self.syntaxError.append((3, self.current_token, self.parseStack[-1]))
                    self.parseStack.pop()
                    node = self.parseTreeStack.pop()
                    node.parent = Node("seektir")
                else:
                    terminal = self.parseStack.pop()
                    node: Node = self.parseTreeStack.pop()
                    if node and terminal == TokenType.ID:
                        node.name = '(%s, %s)' % (TokenType.ID.name, self.current_token.lexim)
                    self.go_next_token()
            if self.current_token.token_type == TokenType.EOF and len(self.parseStack) == 1:
                if not self.syntaxError or self.syntaxError[-1][0] != 4:
                    Node('$', parent=self.parseTree)
                break

    def next_move(self, token_pack: TokenPack):
        token = token_pack.token_type
        lexim = token_pack.lexim
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
            node = Node('(%s, %s)' % (arg.name, token.lexim), parent=parent)
        elif arg in KEYWORDS:
            node = Node('(%s, %s)' % (TokenType.KEYWORD.name, arg), parent=parent)
        else:
            node = Node('(%s, %s)' % (TokenType.SYMBOL.name, arg), parent=parent)
        return node

    def same_terminal(self, token_pack):
        token = token_pack.token_type
        lexim = token_pack.lexim
        if token in (TokenType.KEYWORD, TokenType.SYMBOL):
            return self.parseStack[-1] == lexim
        else:
            return self.parseStack[-1] == token

    def panic_mode(self, token_pack):
        if token_pack.token_type == TokenType.EOF:
            self.syntaxError.append((4, token_pack))  # errorType , (lineno, token)
            self.parseStack.clear()
            for node in self.parseTreeStack:
                if node:
                    node.parent = Node("seektir")
            self.parseStack.append(TokenType.EOF)
        else:
            self.syntaxError.append((1, token_pack))
            self.go_next_token()

    def derivate_non_terminal(self, token_pack):
        next_branch = self.next_move(token_pack)
        if next_branch is None:
            self.panic_mode(token_pack)
        elif next_branch == -1:
            self.syntaxError.append((2, token_pack, self.parseStack[-1]))
            self.parseStack.pop()
            node = self.parseTreeStack.pop()
            node.parent = Node("seektir")
        else:
            parent = self.parseTreeStack[-1]
            self.parseTreeStack.pop()
            self.parseStack.pop()
            if next_branch == () or (len(next_branch) == 1 and isinstance(next_branch[0], ActionSymbols)):
                Node(EPSILON, parent=parent)
            nodes = []
            for arg in next_branch:
                if isinstance(arg, ActionSymbols):
                    nodes.append(Node(str(arg), parent=parent))
                else:
                    nodes.append(self.make_node(arg, token_pack, parent))
            for arg, node in zip(next_branch[::-1], nodes[::-1]):
                self.parseStack.append(arg)
                self.parseTreeStack.append(node)

    def go_next_token(self):
        result, self.lookahead = self.scanner.get_next_token(self.lookahead)
        self.current_token = result
        return result


class ParseTable:
    next = {
        (NonTerminal.Program, 'break'): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, 'continue'): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, TokenType.ID): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, 'return'): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, 'global'): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, 'def'): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, 'if'): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, 'while'): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),
        (NonTerminal.Program, TokenType.EOF): (NonTerminal.Statements, ActionSymbols.PROGRAM_DONE),

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
        (NonTerminal.Simple_stmt, 'break'): ('break', ActionSymbols.LoopBreak),
        (NonTerminal.Simple_stmt, 'continue'): ('continue', ActionSymbols.LoopContinue),
        (NonTerminal.Simple_stmt, TokenType.ID): (NonTerminal.Assignment_Call,),
        (NonTerminal.Simple_stmt, 'return'): (NonTerminal.Return_stmt,),
        (NonTerminal.Simple_stmt, 'global'): (NonTerminal.Global_stmt,),

        (NonTerminal.Compound_stmt, ';'): -1,
        (NonTerminal.Compound_stmt, 'def'): (NonTerminal.Function_def,),
        (NonTerminal.Compound_stmt, 'if'): (NonTerminal.If_stmt,),
        (NonTerminal.Compound_stmt, 'while'): (NonTerminal.Iteration_stmt,),

        (NonTerminal.Assignment_Call, ';'): -1,
        (NonTerminal.Assignment_Call, TokenType.ID): (ActionSymbols.PID, TokenType.ID, NonTerminal.B),

        (NonTerminal.B, ';'): -1,
        (NonTerminal.B, '='): ('=', NonTerminal.C),
        (NonTerminal.B, '['): (
            '[', NonTerminal.Expression, ActionSymbols.LIST_OFFSET, ']',
            '=', NonTerminal.C),
        (NonTerminal.B, '('): (
            '(', ActionSymbols.FuncCallStart, NonTerminal.Arguments, ActionSymbols.FuncCallEnd2, ')'),

        (NonTerminal.C, ';'): -1,
        (NonTerminal.C, TokenType.ID): (NonTerminal.Expression, ActionSymbols.ASSIGN),
        (NonTerminal.C, TokenType.NUM): (NonTerminal.Expression, ActionSymbols.ASSIGN),
        (NonTerminal.C, '['): (ActionSymbols.LIST_TYPE,
                               '[', NonTerminal.Expression, ActionSymbols.LIST_ASSIGN, NonTerminal.List_Rest, ']',
                               ActionSymbols.LIST_END_ASSIGN),

        (NonTerminal.List_Rest, ']'): (),
        (NonTerminal.List_Rest, ','): (',', NonTerminal.Expression, ActionSymbols.LIST_ASSIGN, NonTerminal.List_Rest),

        (NonTerminal.Return_stmt, ';'): -1,
        (NonTerminal.Return_stmt, 'return'): ('return', NonTerminal.Return_Value, ActionSymbols.FuncJBack),
        (NonTerminal.Return_Value, ';'): (),
        (NonTerminal.Return_Value, TokenType.ID): (NonTerminal.Expression, ActionSymbols.FuncStoreRV),
        (NonTerminal.Return_Value, TokenType.NUM): (NonTerminal.Expression, ActionSymbols.FuncStoreRV),

        (NonTerminal.Global_stmt, ';'): -1,
        (NonTerminal.Global_stmt, 'global'): ('global', ActionSymbols.GID, TokenType.ID),

        (NonTerminal.Function_def, ';'): -1,
        (NonTerminal.Function_def, 'def'): (
            'def', ActionSymbols.FuncDef, TokenType.ID,
            '(', NonTerminal.Params, ')', ':',
            NonTerminal.Statements, ActionSymbols.FuncEnd),

        (NonTerminal.Params, ')'): (),
        (NonTerminal.Params, TokenType.ID): (ActionSymbols.FuncPID, TokenType.ID, NonTerminal.Params_Prime),
        (NonTerminal.Params_Prime, ')'): (),
        (NonTerminal.Params_Prime, ','): (',', ActionSymbols.FuncPID, TokenType.ID, NonTerminal.Params_Prime),

        # if else while blocks
        (NonTerminal.If_stmt, ';'): -1,
        (NonTerminal.Iteration_stmt, ';'): -1,
        (NonTerminal.Else_block, ';'): (ActionSymbols.JHere,),
        (NonTerminal.If_stmt, 'if'): (
            'if', NonTerminal.Relational_Expression, ActionSymbols.JFalse, ':', NonTerminal.Statements,
            NonTerminal.Else_block),
        (NonTerminal.Else_block, 'else'): (
            'else', ActionSymbols.JTrue, ':', NonTerminal.Statements, ActionSymbols.Endif),
        (NonTerminal.Iteration_stmt, 'while'): (
            ActionSymbols.StartLoop, 'while', '(',
            NonTerminal.Relational_Expression,
            ActionSymbols.CheckCond, ')',
            NonTerminal.Statements, ActionSymbols.EndLoop),

        (NonTerminal.Relational_Expression, ')'): -1,
        (NonTerminal.Relational_Expression, ':'): -1,
        (NonTerminal.Relational_Expression, TokenType.ID): (
            NonTerminal.Expression, ActionSymbols.SaveRelop, NonTerminal.Relop, NonTerminal.Expression,
            ActionSymbols.RelopAct),
        (NonTerminal.Relational_Expression, TokenType.NUM): (
            NonTerminal.Expression, ActionSymbols.SaveRelop, NonTerminal.Relop, NonTerminal.Expression,
            ActionSymbols.RelopAct),

        (NonTerminal.Relop, TokenType.ID): -1,
        (NonTerminal.Relop, TokenType.NUM): -1,
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
        (NonTerminal.Expression, TokenType.NUM): (NonTerminal.Term, NonTerminal.Expression_Prime),

        (NonTerminal.Expression_Prime, ';'): (),
        (NonTerminal.Expression_Prime, ']'): (),
        (NonTerminal.Expression_Prime, ')'): (),
        (NonTerminal.Expression_Prime, ','): (),
        (NonTerminal.Expression_Prime, ':'): (),
        (NonTerminal.Expression_Prime, '=='): (),
        (NonTerminal.Expression_Prime, '<'): (),
        (NonTerminal.Expression_Prime, '+'): ('+', NonTerminal.Term, ActionSymbols.ADD, NonTerminal.Expression_Prime),
        (NonTerminal.Expression_Prime, '-'): ('-', NonTerminal.Term, ActionSymbols.SUB, NonTerminal.Expression_Prime),

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
        (NonTerminal.Term, TokenType.NUM): (NonTerminal.Factor, NonTerminal.Term_Prime),

        (NonTerminal.Term_Prime, ';'): (),
        (NonTerminal.Term_Prime, ']'): (),
        (NonTerminal.Term_Prime, ')'): (),
        (NonTerminal.Term_Prime, ','): (),
        (NonTerminal.Term_Prime, ':'): (),
        (NonTerminal.Term_Prime, '=='): (),
        (NonTerminal.Term_Prime, '<'): (),
        (NonTerminal.Term_Prime, '+'): (),
        (NonTerminal.Term_Prime, '-'): (),
        (NonTerminal.Term_Prime, '*'): ('*', NonTerminal.Factor, ActionSymbols.MULT, NonTerminal.Term_Prime),

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
        (NonTerminal.Factor, TokenType.NUM): (NonTerminal.Atom, NonTerminal.Power),

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
        (NonTerminal.Power, '**'): ('**', NonTerminal.Factor, ActionSymbols.Power),

        (NonTerminal.Primary, ';'): (),
        (NonTerminal.Primary, '['): (ActionSymbols.LIST_TYPE2,
                                     '[', NonTerminal.Expression, ActionSymbols.LIST_OFFSET2, ']', NonTerminal.Primary),
        (NonTerminal.Primary, ']'): (),
        (NonTerminal.Primary, '('): ('(', ActionSymbols.FuncCallStart,
                                     NonTerminal.Arguments,
                                     ActionSymbols.FuncCallEnd, ')', NonTerminal.Primary),
        (NonTerminal.Primary, ')'): (),
        (NonTerminal.Primary, ','): (),
        (NonTerminal.Primary, ':'): (),
        (NonTerminal.Primary, '=='): (),
        (NonTerminal.Primary, '<'): (),
        (NonTerminal.Primary, '+'): (),
        (NonTerminal.Primary, '-'): (),
        (NonTerminal.Primary, '*'): (),

        (NonTerminal.Arguments, ')'): (),
        (NonTerminal.Arguments, TokenType.ID): (NonTerminal.Expression, ActionSymbols.FuncSaveArgs,
                                                NonTerminal.Arguments_Prime),
        (NonTerminal.Arguments, TokenType.NUM): (NonTerminal.Expression, ActionSymbols.FuncSaveArgs,
                                                 NonTerminal.Arguments_Prime),

        (NonTerminal.Arguments_Prime, ')'): (),
        (NonTerminal.Arguments_Prime, ','): (',', NonTerminal.Expression, ActionSymbols.FuncSaveArgs,
                                             NonTerminal.Arguments_Prime),

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
        (NonTerminal.Atom, TokenType.ID): (ActionSymbols.PID2, TokenType.ID,),
        (NonTerminal.Atom, TokenType.NUM): (ActionSymbols.PNUM, TokenType.NUM,)
    }
