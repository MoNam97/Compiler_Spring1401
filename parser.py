
from collections import deque
from scanner import Scanner
from utils import TokenType, NonTerminal
from anytree import Node, RenderTree
class ParseTable:
    next = {
        (NonTerminal.Program, 'break'):         (NonTerminal.Statements),
        (NonTerminal.Program, 'continue'):      (NonTerminal.Statements),
        (NonTerminal.Program, TokenType.ID):    (NonTerminal.Statements),
        (NonTerminal.Program, 'return'):        (NonTerminal.Statements),
        (NonTerminal.Program, 'global'):        (NonTerminal.Statements),
        (NonTerminal.Program, 'def'):           (NonTerminal.Statements),
        (NonTerminal.Program, 'if'):            (NonTerminal.Statements),
        (NonTerminal.Program, 'while'):         (NonTerminal.Statements),
        (NonTerminal.Program, TokenType.EOF):   (NonTerminal.Statements),
        
        (NonTerminal.Statements, ';'):          (),
        (NonTerminal.Statements, 'else'):       (),
        (NonTerminal.Statements, TokenType.EOF):(),
        (NonTerminal.Statements, 'break'):      (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'continue'):   (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, TokenType.ID): (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'return'):     (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'global'):     (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'def'):        (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'if'):         (NonTerminal.Statement, ';', NonTerminal.Statements),
        (NonTerminal.Statements, 'while'):      (NonTerminal.Statement, ';', NonTerminal.Statements),
        
        (NonTerminal.Statement, ';'):           -1,
        (NonTerminal.Statement, 'break'):       (NonTerminal.Simple_stmt),
        (NonTerminal.Statement, 'continue'):    (NonTerminal.Simple_stmt),
        (NonTerminal.Statement, TokenType.ID):  (NonTerminal.Simple_stmt),
        (NonTerminal.Statement, 'return'):      (NonTerminal.Simple_stmt),
        (NonTerminal.Statement, 'global'):      (NonTerminal.Simple_stmt),
        (NonTerminal.Statement, 'def'):         (NonTerminal.Compound_stmt),
        (NonTerminal.Statement, 'if'):          (NonTerminal.Compound_stmt),
        (NonTerminal.Statement, 'while'):       (NonTerminal.Compound_stmt),
        
        (NonTerminal.Simple_stmt, ';'):         -1,
        (NonTerminal.Simple_stmt, 'break'):     ('break'),
        (NonTerminal.Simple_stmt, 'continue'):  ('continue'),
        (NonTerminal.Simple_stmt, TokenType.ID):(NonTerminal.Assignment_Call),
        (NonTerminal.Simple_stmt, 'return'):    (NonTerminal.Return_stmt),
        (NonTerminal.Simple_stmt, 'global'):    (NonTerminal.Global_stmt),
        
        (NonTerminal.Compound_stmt, ';'):       -1,
        (NonTerminal.Compound_stmt, 'def'):     (NonTerminal.Function_def),     
        (NonTerminal.Compound_stmt, 'if'):      (NonTerminal.If_stmt),
        (NonTerminal.Compound_stmt, 'while'):   (NonTerminal.Iteration_stmt),
        
        (NonTerminal.Assignment_Call, ';'):     -1,
        (NonTerminal.Assignment_Call, TokenType.ID): (TokenType.ID, NonTerminal.B),
        
        (NonTerminal.B, ';'):                   -1,
        (NonTerminal.B, '='):                   ('=', NonTerminal.C),
        (NonTerminal.B, '['):                   ('[', NonTerminal.Expression, ']', '=', NonTerminal.C),
        (NonTerminal.B, '('):                   ('(', NonTerminal.Arguments, ')'),
        
        (NonTerminal.C, ';'):                   -1,
        (NonTerminal.C, TokenType.ID):          (NonTerminal.Expression),
        (NonTerminal.C, TokenType.NUMBER):      (NonTerminal.Expression),
        (NonTerminal.C, '['):                   ('[', NonTerminal.Expression, NonTerminal.List_Rest, ']'),
        
        (NonTerminal.List_Rest, ']'):           (),
        (NonTerminal.List_Rest, ','):           (',', NonTerminal.Expression, NonTerminal.List_Rest),
        
        (NonTerminal.Return_stmt, ';'):         -1,
        (NonTerminal.Return_stmt, 'return'):    ('return', NonTerminal.Return_Value),
        (NonTerminal.Return_Value, ';'):                (),
        (NonTerminal.Return_Value, TokenType.ID):       (NonTerminal.Expression),
        (NonTerminal.Return_Value, TokenType.NUMBER):   (NonTerminal.Expression),
        
        (NonTerminal.Global_stmt, ';'):         -1,
        (NonTerminal.Global_stmt, 'global'):    ('global', TokenType.ID),
        
        (NonTerminal.Function_def, ';'):        -1,
        (NonTerminal.Function_def, 'def'):      ('def', TokenType.ID, '(', NonTerminal.Params, ')', ':', NonTerminal.Statements),
        
        (NonTerminal.Params, ')'):              (),
        (NonTerminal.Params, TokenType.ID):     (TokenType.ID, NonTerminal.Params_Prime),
        (NonTerminal.Params_Prime, ')'):        (),
        (NonTerminal.Params_Prime, ','):        (',', TokenType.ID, NonTerminal.Params_Prime),
        
        # if else while blocks
        (NonTerminal.If_stmt, ';'):             -1,
        (NonTerminal.Iteration_stmt, ';'):      -1,
        (NonTerminal.Else_block, ';'):          (),
        (NonTerminal.If_stmt, 'if'):            ('if', NonTerminal.Relational_Expression, ':', NonTerminal.Statements, NonTerminal.Else_block),
        (NonTerminal.Else_block, 'else'):       ('else', ':', NonTerminal.Statements),
        (NonTerminal.Iteration_stmt, 'while'):  ('while', '(', NonTerminal.Relational_Expression, ')', NonTerminal.Statements),
        
        (NonTerminal.Relational_Expression, ')'):               -1,
        (NonTerminal.Relational_Expression, ':'):               -1,
        (NonTerminal.Relational_Expression, TokenType.ID):      (NonTerminal.Expression, NonTerminal.Relop, NonTerminal.Expression),
        (NonTerminal.Relational_Expression, TokenType.NUMBER):  (NonTerminal.Expression, NonTerminal.Relop, NonTerminal.Expression),
        
        (NonTerminal.Relop, TokenType.ID):      -1,
        (NonTerminal.Relop, TokenType.NUMBER):  -1,
        (NonTerminal.Relop, '=='):              ('=='),
        (NonTerminal.Relop, '<'):               ('<'),
        
        (NonTerminal.Expression, ';'):          -1,
        (NonTerminal.Expression, ']'):          -1,
        (NonTerminal.Expression, ')'):          -1,
        (NonTerminal.Expression, ','):          -1,
        (NonTerminal.Expression, ':'):          -1,
        (NonTerminal.Expression, '=='):         -1,
        (NonTerminal.Expression, '<'):          -1,
        (NonTerminal.Expression, TokenType.ID): (NonTerminal.Term, NonTerminal.Expression_Prime),
        (NonTerminal.Expression, TokenType.NUMBER): (NonTerminal.Term, NonTerminal.Expression_Prime),
        
        (NonTerminal.Expression_Prime, ';'):    (),
        (NonTerminal.Expression_Prime, ']'):    (),
        (NonTerminal.Expression_Prime, ')'):    (),
        (NonTerminal.Expression_Prime, ','):    (),
        (NonTerminal.Expression_Prime, ':'):    (),
        (NonTerminal.Expression_Prime, '=='):   (),
        (NonTerminal.Expression_Prime, '<'):    (),
        (NonTerminal.Expression_Prime, '+'):    ('+', NonTerminal.Term, NonTerminal.Expression_Prime),
        (NonTerminal.Expression_Prime, '-'):    ('+', NonTerminal.Term, NonTerminal.Expression_Prime),
        
        (NonTerminal.Term, ';'):                -1,
        (NonTerminal.Term, ']'):                -1,
        (NonTerminal.Term, ')'):                -1,
        (NonTerminal.Term, ','):                -1,
        (NonTerminal.Term, ':'):                -1,
        (NonTerminal.Term, '=='):               -1,
        (NonTerminal.Term, '<'):                -1,
        (NonTerminal.Term, '+'):                -1,
        (NonTerminal.Term, '-'):                -1,
        (NonTerminal.Term, TokenType.ID):       (NonTerminal.Factor, NonTerminal.Term_Prime),
        (NonTerminal.Term, TokenType.NUMBER):       (NonTerminal.Factor, NonTerminal.Term_Prime),
        
        (NonTerminal.Term_Prime, ';'):          (),
        (NonTerminal.Term_Prime, ']'):          (),
        (NonTerminal.Term_Prime, ')'):          (),
        (NonTerminal.Term_Prime, ','):          (),
        (NonTerminal.Term_Prime, ':'):          (),
        (NonTerminal.Term_Prime, '=='):         (),
        (NonTerminal.Term_Prime, '<'):          (),
        (NonTerminal.Term_Prime, '+'):          (),
        (NonTerminal.Term_Prime, '-'):          (),
        (NonTerminal.Term_Prime, '*'):          ('*', NonTerminal.Factor, NonTerminal.Term_Prime),
        
        (NonTerminal.Factor, ';'):              -1,
        (NonTerminal.Factor, ']'):              -1,
        (NonTerminal.Factor, ')'):              -1,
        (NonTerminal.Factor, ','):              -1,
        (NonTerminal.Factor, ':'):              -1,
        (NonTerminal.Factor, '=='):             -1,
        (NonTerminal.Factor, '<'):              -1,
        (NonTerminal.Factor, '+'):              -1,
        (NonTerminal.Factor, '-'):              -1,
        (NonTerminal.Factor, '*'):              -1,
        (NonTerminal.Factor, TokenType.ID):     (NonTerminal.Atom, NonTerminal.Power),
        (NonTerminal.Factor, TokenType.NUMBER): (NonTerminal.Atom, NonTerminal.Power),
        
        (NonTerminal.Factor, ';'):              (NonTerminal.Primary),
        (NonTerminal.Factor, '['):              (NonTerminal.Primary),
        (NonTerminal.Factor, ']'):              (NonTerminal.Primary),
        (NonTerminal.Factor, '('):              (NonTerminal.Primary),
        (NonTerminal.Factor, ')'):              (NonTerminal.Primary),
        (NonTerminal.Factor, ','):              (NonTerminal.Primary),
        (NonTerminal.Factor, ':'):              (NonTerminal.Primary),
        (NonTerminal.Factor, '=='):             (NonTerminal.Primary),
        (NonTerminal.Factor, '<'):              (NonTerminal.Primary),
        (NonTerminal.Factor, '+'):              (NonTerminal.Primary),
        (NonTerminal.Factor, '-'):              (NonTerminal.Primary),
        (NonTerminal.Factor, '*'):              (NonTerminal.Primary),
        (NonTerminal.Factor, '**'):             ('**', NonTerminal.Factor),
        
        (NonTerminal.Primary, ';'):             (),
        (NonTerminal.Primary, '['):             ('[', NonTerminal.Expression, ']', NonTerminal.Primary),
        (NonTerminal.Primary, ']'):             (),
        (NonTerminal.Primary, '('):             ('(', NonTerminal.Arguments, ')', NonTerminal.Primary),
        (NonTerminal.Primary, ')'):             (),
        (NonTerminal.Primary, ','):             (),
        (NonTerminal.Primary, ':'):             (),
        (NonTerminal.Primary, '=='):            (),
        (NonTerminal.Primary, '<'):             (),
        (NonTerminal.Primary, '+'):             (),
        (NonTerminal.Primary, '-'):             (),
        (NonTerminal.Primary, '*'):             (),
        
        (NonTerminal.Arguments, ')'):           (),
        (NonTerminal.Arguments, TokenType.ID):  (NonTerminal.Expression, NonTerminal.Arguments_Prime),
        (NonTerminal.Arguments, TokenType.NUMBER):(NonTerminal.Expression, NonTerminal.Arguments_Prime),
        
        (NonTerminal.Arguments_Prime, ')'):     (),
        (NonTerminal.Arguments_Prime, ','):     (',', NonTerminal.Expression, NonTerminal.Arguments_Prime),
        
        (NonTerminal.Atom, ';'):                -1,
        (NonTerminal.Atom, '['):                -1,
        (NonTerminal.Atom, ']'):                -1,
        (NonTerminal.Atom, '('):                -1,
        (NonTerminal.Atom, ')'):                -1,
        (NonTerminal.Atom, ','):                -1,
        (NonTerminal.Atom, ':'):                -1,
        (NonTerminal.Atom, '=='):               -1,
        (NonTerminal.Atom, '<'):                -1,
        (NonTerminal.Atom, '+'):                -1,
        (NonTerminal.Atom, '-'):                -1,
        (NonTerminal.Atom, '*'):                -1,
        (NonTerminal.Atom, '**'):               -1,
        (NonTerminal.Atom, TokenType.ID):       (TokenType.ID),
        (NonTerminal.Atom, TokenType.NUMBER):   (TokenType.NUMBER)
    }

class Parser:
    scanner = None
    current_token = None
    parsestack = deque()
    parseTree = None
    
    def __init__(self, filepath, symbol):
        self.scanner = Scanner(filepath, symbol)
        self.parsestack.extend([TokenType.EOF, NonTerminal.Program])
    
    def parse(self):
        lookahead = False
        while True:
            self.current_token, lookahead = self.scanner.get_next_token(lookahead)
            
            if self.current_token[1][0] == TokenType.EOF:
                break