from collections import deque

from py_minus.utils import ActionSymbols

INT_SIZE = 4


class CodeGenerator:
    stack = None
    _while_start = None
    _while_cond_addr = None
    _while_cond_line = None

    def __init__(self):
        self.stack = deque()
        self._while_start = deque()
        self._while_cond_addr = deque()
        self._while_cond_line = deque()
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
        if token_pack.lexim == '==':
            self.stack.append(0)
        elif token_pack.lexim == '<':
            self.stack.append(1)
        else:
            print("not a relop")

    def _handle_relopact(self, _token_pack):
        ######################  THIS could be handled with _handle_arithmethic
        operand2 = self.stack.pop()
        operator = self.stack.pop()
        operand1 = self.stack.pop()
        addr = self._get_temp_address()
        if operator == 0:
            self.pb.append(f"(EQ, {operand1}, {operand2}, {addr})")
        elif operator == 1:
            self.pb.append(f"(LT, {operand1}, {operand2}, {addr})")
        else:
            print("Relational_Expression Bug. Relop not set")
        self.stack.append(addr)
        self.temp_mem = None

    def _handle_j_false(self, _token_pack):
        self.stack.append(len(self.pb))
        self.pb.append("placeholder jump jfalse")

    def _handle_JTrue(self, _token_pack):
        i = self.stack.pop()
        cond = self.stack.pop()
        self.pb[i] = f"(JPF, {cond}, {len(self.pb) + 1}, )"
        self.stack.append(len(self.pb))
        self.pb.append("placeholder jump jtrue")

    def _handle_Endif(self, _token_pack):
        i = self.stack.pop()
        self.pb[i] = f"(JP, {len(self.pb)}, , )"

    def _handle_JHere(self, _token_pack):
        i = self.stack.pop()
        cond = self.stack.pop()
        self.pb[i] = f"(JPF, {cond}, {len(self.pb)}, )"

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

    def _handle_start_loop(self, _token_pack):
        self._while_start.append(len(self.pb))
        self.stack.append(len(self.pb))

    def _handle_check_cond(self, _token_pack):
        self._while_cond_addr.append(self.stack[-1])
        self._while_cond_line.append(len(self.pb))
        self.stack.append(len(self.pb))
        self.pb.append("placeholder while")

    def _handle_end_loop(self, _token_pack):
        jump_pb = self.stack.pop()
        temp_cond_addr = self.stack.pop()
        while_start = self.stack.pop()
        self.pb.append(f"(JP, {while_start}, , )")
        self.pb[jump_pb] = f"(JPF, {temp_cond_addr}, {len(self.pb)}, )"
        self._while_start.pop()
        self._while_cond_addr.pop()
        self._while_cond_line.pop()

    def _handle_loop_break(self, _token_pack):
        self.pb.append(f"(ASSIGN, #0, {self._while_cond_addr[-1]}, )")
        self.pb.append(f"(JP, {self._while_cond_line[-1]}, , )")

    def _handle_loop_continue(self, _token_pack):
        self.pb.append(f"(JP, {self._while_start[-1]}, , )")

    def handle(self, action_symbol, token_pack):
        handlers = {
            ActionSymbols.PID: self._handle_pid,
            ActionSymbols.PNUM: self._handle_pnum,
            ActionSymbols.MULT: self._handle_mult,
            ActionSymbols.SUB: self._handle_sub,
            ActionSymbols.ADD: self._handle_add,
            ActionSymbols.ASSIGN: self._handle_assign,
            ActionSymbols.SaveRelop: self._handle_saverelop,
            ActionSymbols.RelopAct: self._handle_relopact,
            ActionSymbols.JFalse: self._handle_j_false,
            ActionSymbols.JTrue: self._handle_JTrue,
            ActionSymbols.Endif: self._handle_Endif,
            ActionSymbols.JHere: self._handle_JHere,

            ActionSymbols.StartLoop: self._handle_start_loop,
            ActionSymbols.CheckCond: self._handle_check_cond,
            ActionSymbols.EndLoop: self._handle_end_loop,
            ActionSymbols.LoopBreak: self._handle_loop_break,
            ActionSymbols.LoopContinue: self._handle_loop_continue,
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