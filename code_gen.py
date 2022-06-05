from collections import deque

from utils import ActionSymbols

INT_SIZE = 4


class CodeGenerator:
    stack = None
    temp_mem = None

    def __init__(self):
        self.stack = deque()
        self.pb = []
        self.last_temp = 500
        self.last_variable = 100
        self.symbol_table = {}

    def _get_temp_address(self):
        self.last_temp += INT_SIZE
        return self.last_temp - INT_SIZE

    def _get_var_address(self):
        self.last_variable += INT_SIZE
        return self.last_variable - INT_SIZE

    def _find_addr(self, name):
        if name in self.symbol_table:
            return self.symbol_table[name]
        addr = self._get_var_address()
        self.symbol_table[name] = addr
        return addr

    def _handle_pid(self, token_pack):
        addr = self._find_addr(token_pack.lexim)
        self.stack.append(addr)

    def _handle_pnum(self, token_pack):
        addr = self._get_temp_address()
        self.stack.append(addr)
        self.pb.append(f"(ASSIGN, #{token_pack.lexim}, {addr}, )")

    def _handle_saverelop(self, token_pack):
        self.temp_mem = token_pack.lexim

    def _handle_relopact(self):
        ######################  THIS could be handled with _handle_arithmethic
        operand2 = self.stack.pop()
        operand1 = self.stack.pop()
        addr = self._get_temp_address()
        if self.temp_mem == '==':
            self.pb.append(f"(EQ, {operand1}, {operand2}, {addr})")
        elif self.temp_mem == '<':
            self.pb.append(f"(LT, {operand1}, {operand2}, {addr})")
        else:
            print("Relational_Expression Bug. Relop not set")
        self.stack.append(addr)
        self.temp_mem = None

    def _handle_arithmethic(self, operator):
        operand2 = self.stack.pop()
        operand1 = self.stack.pop()
        addr = self._get_temp_address()
        self.pb.append(f"({operator}, {operand1}, {operand2}, {addr})")
        self.stack.append(addr)

    def _handle_add(self, _token_pack):
        self._handle_arithmethic("ADD")

    def _handle_sub(self, _token_pack):
        self._handle_arithmethic("SUB")

    def _handle_mult(self, _token_pack):
        self._handle_arithmethic("MULT")

    def _handle_assign(self, _token_pack):
        operand1 = self.stack.pop()
        operand2 = self.stack.pop()
        self.pb.append(f"(ASSIGN, {operand1}, {operand2}, )")

    def handle(self, action_symbol, token_pack):
        handlers = {
            ActionSymbols.PID: self._handle_pid,
            ActionSymbols.PNUM: self._handle_pnum,
            ActionSymbols.MULT: self._handle_mult,
            ActionSymbols.SUB: self._handle_sub,
            ActionSymbols.ADD: self._handle_add,
            ActionSymbols.ASSIGN: self._handle_assign,
            ActionSymbols.SaveRelop: self._handle_saverelop,
            ActionSymbols.RelopAct: self._handle_relopact
        }
        if action_symbol not in handlers:
            print(f"Error: Unexpected actionsymbol {action_symbol}")
            return
        handler = handlers[action_symbol]
        handler(token_pack)

    def print(self):
        for idx, code in enumerate(self.pb):
            print(f"{idx}\t{code}")
        print(f"{len(self.pb)}\t(PRINT, {list(self.symbol_table.items())[-1][1]}, , )")
