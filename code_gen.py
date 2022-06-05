from collections import deque

from utils import ActionSymbols


class CodeGenerator:
    stack = None

    def __init__(self):
        self.stack = deque()
        self.pb = []
        self.last_temp = 500

    def _get_temp_address(self):
        self.last_temp += 4
        return self.last_temp - 4

    def _find_addr(self, name):
        return 100

    def _handle_pid(self, token_pack):
        addr = self._find_addr(token_pack)
        self.stack.append(addr)

    def _handle_pnum(self, token_pack):
        addr = self._get_temp_address()
        self.stack.append(addr)
        self.pb.append(f"(ASSIGN, #{token_pack.lexim}, {addr},)")

    def _handle_arithmethic(self, operator):
        operand1 = self.stack.pop()
        operand2 = self.stack.pop()
        addr = self._get_temp_address()
        self.pb.append(f"({operator}, {operand1}, {operand2}, {addr})")
        self.stack.append(addr)

    def _handle_add(self, _token_pack):
        self._handle_arithmethic("ADD")

    def _handle_sub(self, _token_pack):
        self._handle_arithmethic("SUB")

    def _handle_mult(self, _token_pack):
        self._handle_arithmethic("MULT")

    def handle(self, action_symbol, token_pack):
        handlers = {
            ActionSymbols.PID: self._handle_pid,
            ActionSymbols.PNUM: self._handle_pnum,
            ActionSymbols.MULT: self._handle_mult,
            ActionSymbols.SUB: self._handle_sub,
            ActionSymbols.ADD: self._handle_add,
        }
        if action_symbol not in handlers:
            print(f"Error: Unexpected actionsymbol {action_symbol}")
            return
        handler = handlers[action_symbol]
        handler(token_pack)
