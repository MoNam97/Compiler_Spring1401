import sys
from collections import deque

from py_minus.utils import ActionSymbols, SymbolTable, SymbolTableItem, FunctionData, ListData

INT_SIZE = 4


class CodeGenerator:
    stack = None
    if_stack = None
    func_stack = None
    list_stack = None
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
        self.list_stack = deque()
        self._while_start = deque()
        self._while_cond_addr = deque()
        self._while_cond_line = deque()
        self.last_temp = 500
        self.last_variable = 100
        self.pb = [
            f"(JP, 3, , )",
        ]
        self.initialize_output_function()

    def initialize_output_function(self):
        ra = self._get_temp_address()
        rv = self._get_temp_address()
        inp = self._get_var_address()

        self.symbol_table.items.append(
            SymbolTableItem(
                lexim='output',
                addr=len(self.pb),
                type=FunctionData(
                    addr=len(self.pb),
                    ra=ra,
                    rv=rv,
                    args=[inp]
                ),
                scope=self.scope
            ))
        self.pb.extend([
            f"(PRINT, {inp}, , )",
            f"(JP, @{ra}, , )",
        ])

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

    def _reverse_find_addr(self, name):
        for item in self.symbol_table.items:
            if name == item.lexim:
                return item
        return None

    def _handle_pid(self, token_pack):
        addr = self._find_addr(token_pack.lexim)
        self.stack.append(addr)

    def _handle_gid(self, token_pack):
        item = self._reverse_find_addr(token_pack.lexim)
        self.symbol_table.items.append(item)

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

    def _handle_j_true(self, _token_pack):
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

    def _handle_power(self, _token_pack):
        result = self._get_temp_address()
        temp1 = self._get_temp_address()
        temp2 = self._get_temp_address()
        power = self.stack.pop()
        number = self.stack.pop()
        self.pb.append(f"(ASSIGN, #1, {result}, )")
        self.pb.append(f"(JPF, {power}, {len(self.pb) + 6}, )")
        self.pb.append(f"(MULT, {result}, {number}, {temp1})")
        self.pb.append(f"(ASSIGN, {temp1}, {result}, )")
        self.pb.append(f"(SUB, {power}, #1, {temp2})")
        self.pb.append(f"(ASSIGN, {temp2}, {power}, )")
        self.pb.append(f"(JP, {len(self.pb) - 5}, , )")
        self.stack.append(result)

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
        self.func_stack.append(len(self.pb))
        self.pb.append("placeholder of jump to end of the func")
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
        addr = self.func_stack.pop()
        self.pb[addr] = f"(JP, {len(self.pb)}, , )"

    def _handle_func_call_start(self, _token_pack):
        self.func_stack.append(0)

    def _handle_func_call_end(self, _token_pack, store_result=True):
        func_addr = self.stack.pop()
        self.func_stack.pop()
        func_data = self._find_func_data(func_addr)
        self.pb.append(f"(ASSIGN, #{len(self.pb) + 2}, {func_data.ra}, )")
        self.pb.append(f"(JP, {func_data.addr}, , )")
        if store_result:
            temp_addr = self._get_temp_address()
            self.stack.append(temp_addr)
            self.pb.append(f"(ASSIGN, {func_data.rv}, {temp_addr}, )")

    def _handle_func_call_end2(self, _token_pack):
        self._handle_func_call_end(_token_pack, store_result=False)

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
        item = self.symbol_table.find_by_addr(func_addr)
        assert item is not None
        func_data = item.type
        assert func_data is not None
        assert isinstance(func_data, FunctionData)
        return func_data

    def _handle_list_type(self, _token_pack):
        addr = self.stack.pop()
        symbol_item = self.symbol_table.find_by_addr(addr=addr)
        if symbol_item.type is None:
            # TODO: Int and temporary None could be misused here
            symbol_item.type = ListData(self._get_temp_address(), self._get_temp_address())
            assert isinstance(symbol_item.type, ListData)
            self.pb.append(f"(ASSIGN, #{symbol_item.type.first}, {addr}, )")
        self.list_stack.append(symbol_item.type)

    def _handle_list_type2(self, _token_pack):
        # addr = self.stack.pop()
        # symbol_item = self.symbol_table.find_by_addr(addr=addr)
        # assert isinstance(symbol_item.type, ListData)
        # self.list_stack.append(symbol_item.type)
        pass

    def _handle_list_assign(self, _token_pack):
        exp_addr = self.stack.pop()
        list_data = self.list_stack.pop()
        new_list_data = ListData(self._get_temp_address(), self._get_temp_address())
        self.pb.append(f"(ASSIGN, {exp_addr}, {list_data.first}, )")
        self.pb.append(f"(ASSIGN, #{new_list_data.first}, {list_data.rest}, )")
        self.list_stack.append(new_list_data)

    def _handle_list_end_assign(self, _token_pack):
        self.list_stack.pop()

    def _handle_list_offset(self, _token_pack):
        temp1 = self._get_temp_address()
        temp2 = self._get_temp_address()
        exp_addr = self.stack.pop()
        addr = self.stack.pop()
        # TODO: Complex lists are ignored (i.e. [0, [0, 1], [1, 3], 1*4])
        self.pb.append(f"(MULT, #{3 * INT_SIZE}, {exp_addr}, {temp1})")
        self.pb.append(f"(ADD, {temp1}, {addr}, {temp2})")
        self.stack.append(f"@{temp2}")

    def _handle_list_offset2(self, _token_pack):
        temp1 = self._get_temp_address()
        temp2 = self._get_temp_address()
        exp_addr = self.stack.pop()
        addr = self.stack.pop()
        # TODO: Complex lists are ignored (i.e. [0, [0, 1], [1, 3], 1*4])
        self.pb.append(f"(MULT, #{3 * INT_SIZE}, {exp_addr}, {temp1})")
        self.pb.append(f"(ADD, {temp1}, {addr}, {temp2})")
        self.pb.append(f"(ASSIGN, @{temp2}, {temp1}, )")
        self.stack.append(temp1)

    def handle(self, action_symbol, token_pack):
        handlers = {
            ActionSymbols.PID: self._handle_pid,
            ActionSymbols.GID: self._handle_gid,
            ActionSymbols.PNUM: self._handle_pnum,
            ActionSymbols.MULT: self._handle_mult,
            ActionSymbols.SUB: self._handle_sub,
            ActionSymbols.ADD: self._handle_add,
            ActionSymbols.Power: self._handle_power,
            ActionSymbols.ASSIGN: self._handle_assign,
            ActionSymbols.SaveRelop: self._handle_saverelop,
            ActionSymbols.RelopAct: self._handle_relopact,
            ActionSymbols.JFalse: self._handle_j_false,
            ActionSymbols.JTrue: self._handle_j_true,
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
            ActionSymbols.FuncCallEnd2: self._handle_func_call_end2,
            ActionSymbols.FuncSaveArgs: self._handle_func_save_args,
            ActionSymbols.FuncStoreRV: self._handle_func_store_rv,
            ActionSymbols.FuncJBack: self._handle_func_j_back,

            ActionSymbols.LIST_TYPE: self._handle_list_type,
            ActionSymbols.LIST_TYPE2: self._handle_list_type2,
            ActionSymbols.LIST_OFFSET: self._handle_list_offset,
            ActionSymbols.LIST_OFFSET2: self._handle_list_offset2,
            ActionSymbols.LIST_ASSIGN: self._handle_list_assign,
            ActionSymbols.LIST_END_ASSIGN: self._handle_list_end_assign,
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

    def print(self, file=sys.stdout):
        assert self.scope == 0
        assert len(self.stack) == 0
        assert len(self.if_stack) == 0
        assert len(self.func_stack) == 0
        main_addr = self._find_addr('main')
        func_data = self._find_func_data(main_addr)
        pb = self.pb.copy()
        pb.append(f"(ASSIGN, #{len(self.pb) + 2}, {func_data.ra}, )")
        pb.append(f"(JP, {main_addr}, , )")
        pb.append("(ASSIGN, #1, 100, )")
        for idx, code in enumerate(pb):
            print(f"{idx}\t{code}", file=file)
