from collections import deque

from py_minus.utils import ActionSymbols, SymbolTable, SymbolTableItem, FunctionData

INT_SIZE = 4


# TODO: Consider if and return confilicts

class CodeGenerator:
    stack = None
    if_stack = None
    func_stack = None
    _while_start = None
    _while_cond_addr = None
    _while_cond_line = None

    symbol_table = None
    scope = 0

    def __init__(self):
        self.symbol_table = SymbolTable(items=[])
        self.stack = deque()
        self.if_stack = deque()
        self.func_stack = deque()
        self._while_start = deque()
        self._while_cond_addr = deque()
        self._while_cond_line = deque()
        self.pb = [f"(JP, 21, , )"]
        self.last_temp = 500
        self.last_variable = 100

    def _get_temp_address(self):
        self.last_temp += INT_SIZE
        return self.last_temp - INT_SIZE

    def _get_var_address(self):
        self.last_variable += INT_SIZE
        return self.last_variable - INT_SIZE

    def _find_addr(self, name):
        for item in self.symbol_table.items[::-1]:
            if name == item.lexim:
                return item.addr
        addr = self._get_var_address()
        self.symbol_table.items.append(SymbolTableItem(
            lexim=name,
            addr=addr,
            type=None,
            scope=self.scope
        ))
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
        self.if_stack.append(self.stack.pop())
        self.if_stack.append(len(self.pb))
        self.pb.append("placeholder jump jfalse")
        self.increase_scope()

    def _handle_JTrue(self, _token_pack):
        self.decrease_scope()
        i = self.if_stack.pop()
        cond = self.if_stack.pop()
        self.pb[i] = f"(JPF, {cond}, {len(self.pb) + 1}, )"
        self.if_stack.append(len(self.pb))
        self.pb.append("placeholder jump jtrue")
        self.increase_scope()

    def _handle_Endif(self, _token_pack):
        i = self.if_stack.pop()
        self.pb[i] = f"(JP, {len(self.pb)}, , )"
        self.decrease_scope()

    def _handle_JHere(self, _token_pack):
        i = self.if_stack.pop()
        cond = self.if_stack.pop()
        self.pb[i] = f"(JPF, {cond}, {len(self.pb)}, )"
        self.decrease_scope()

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
        self.increase_scope()

    def _handle_end_loop(self, _token_pack):
        jump_pb = self.stack.pop()
        temp_cond_addr = self.stack.pop()
        while_start = self.stack.pop()
        self.pb.append(f"(JP, {while_start}, , )")
        self.pb[jump_pb] = f"(JPF, {temp_cond_addr}, {len(self.pb)}, )"
        self._while_start.pop()
        self._while_cond_addr.pop()
        self._while_cond_line.pop()
        self.decrease_scope()

    def _handle_loop_break(self, _token_pack):
        self.pb.append(f"(ASSIGN, #0, {self._while_cond_addr[-1]}, )")
        self.pb.append(f"(JP, {self._while_cond_line[-1]}, , )")

    def _handle_loop_continue(self, _token_pack):
        self.pb.append(f"(JP, {self._while_start[-1]}, , )")

    def _handle_func_def(self, token_pack):
        ra = self._get_temp_address()
        rv = self._get_temp_address()
        self.func_stack.append(len(self.symbol_table.items))
        self.symbol_table.items.append(
            SymbolTableItem(
                lexim=token_pack.lexim,
                addr=len(self.pb),
                type=FunctionData(
                    addr=len(self.pb),
                    ra=ra,
                    rv=rv,
                    args=[]
                ),
                scope=self.scope
            ))
        self.increase_scope()

    def _handle_func_pid(self, token_pack):
        addr = self._find_addr(token_pack.lexim)
        assert isinstance(self.symbol_table.items[self.func_stack[-1]].type, FunctionData)
        self.symbol_table.items[self.func_stack[-1]].type.args.append(addr)

    def _handle_func_end(self, _token_pack):
        func_idx = self.func_stack.pop()
        ra = self.symbol_table.items[func_idx].type.ra
        self.pb.append(f"(JP, @{ra}, , )")
        self.decrease_scope()

    def _handle_func_call_start(self, _token_pack):
        self.func_stack.append(0)

    def _handle_func_call_end(self, _token_pack):
        func_addr = self.stack.pop()
        self.func_stack.pop()
        func_data = self._find_func_data(func_addr)
        self.stack.append(func_data.rv)
        self.pb.append(f"(ASSIGN, #{len(self.pb) + 2}, {func_data.ra}, )")
        self.pb.append(f"(JP, {func_data.addr}, , )")

    def _handle_func_save_args(self, _token_pack):
        arg_addr = self.stack.pop()
        idx = self.func_stack[-1]
        func_addr = self.stack[-1]
        func_data = self._find_func_data(func_addr)
        self.pb.append(f"(ASSIGN, {arg_addr}, {func_data.args[idx]}, )")
        self.func_stack[-1] += 1

    def _handle_func_j_back(self, _token_pack):
        func_idx = self.func_stack[-1]
        ra = self.symbol_table.items[func_idx].type.ra
        self.pb.append(f"(JP, @{ra}, , )")

    def _handle_func_store_rv(self, _token_pack):
        addr = self.stack.pop()
        func_idx = self.func_stack[-1]
        self.pb.append(f"(ASSIGN, {addr}, {self.symbol_table.items[func_idx].type.rv}, )")

    def _find_func_data(self, func_addr):
        func_data = None
        for item in self.symbol_table.items[::-1]:
            if func_addr == item.addr:
                func_data = item.type
        assert func_data is not None
        assert isinstance(func_data, FunctionData)
        return func_data

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

            ActionSymbols.FuncDef: self._handle_func_def,
            ActionSymbols.FuncPID: self._handle_func_pid,
            ActionSymbols.FuncEnd: self._handle_func_end,
            ActionSymbols.FuncCallStart: self._handle_func_call_start,
            ActionSymbols.FuncCallEnd: self._handle_func_call_end,
            ActionSymbols.FuncSaveArgs: self._handle_func_save_args,
            ActionSymbols.FuncStoreRV: self._handle_func_store_rv,
            ActionSymbols.FuncJBack: self._handle_func_j_back,
        }
        if action_symbol not in handlers:
            print(f"Error: Unexpected actionsymbol {action_symbol}")
            return
        handler = handlers[action_symbol]
        handler(token_pack)

    def increase_scope(self):
        self.scope += 1

    def decrease_scope(self):
        for idx, item in enumerate(self.symbol_table.items):
            if item.scope == self.scope:
                self.symbol_table.items = self.symbol_table.items[0:idx]
                break
        self.scope -= 1

    def print(self):
        assert self.scope == 0
        assert len(self.stack) == 0
        assert len(self.if_stack) == 0
        assert len(self.func_stack) == 0

        for idx, code in enumerate(self.pb):
            print(f"{idx}\t{code}")
        print(f"{len(self.pb)}\t(PRINT, {self.symbol_table.items[-1].addr}, , )")
