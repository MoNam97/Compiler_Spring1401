from queue import Queue

from utils import ActionSymbols


class CodeGenerator:
    def __init__(self):
        self.stack = Queue()

    def _find_addr(self, name):
        return 100

    def _handle_pid(self, token_pack):
        addr = self._find_addr(token_pack)
        self.stack.put(addr)

    def _handle_num(self, token_pack):
        self.stack.put(int(token_pack.lexim))

    def handle(self, action_symbol, token_pack):
        handlers = {
            ActionSymbols.PID: self._handle_pid,
            ActionSymbols.NUM: self._handle_num,
        }
        if action_symbol not in handlers:
            print(f"Error: Unexpected actionsymbol {action_symbol}")
            return
        handler = handlers[action_symbol]
        handler(token_pack)
