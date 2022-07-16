import re


class Optimizer:
    code_gen_pb = None
    pb = None
    code_blocks = []
    mem_value = {}
    useless_mem = []
    pb_changed = False
    sblocks = {}

    def __init__(self, pb):
        self.code_gen_pb = pb
        self.pb = pb.copy()
        self.pb_changed = True

    def simple_optimization(self):
        self.constant_copy_propagation()
        self.delete_deadlines()

    def deep_optimization(self):
        while self.pb_changed:
            self.constant_copy_propagation()
            self.constant_folding()
        self.delete_deadlines()

    def set_mem_values(self):
        self.mem_value = {}
        for i in range(len(self.pb)):
            current_code = re.split(r',', self.pb[i].strip('()'))
            if current_code[0] == 'ASSIGN':
                token = ' ' + current_code[2].strip(' @')
                if re.match(r"#*\d+", current_code[1].strip()):
                    if token in self.mem_value:
                        self.mem_value[token] = 'complex'
                    else:
                        self.mem_value[token] = current_code[1]
                else:
                    self.mem_value[token] = 'complex'
            if current_code[0] in ['ADD', 'MULT', 'SUB', 'EQ', 'LT']:
                self.mem_value[' ' + current_code[3].strip(' @')] = 'complex'

        for i in self.mem_value:
            if self.mem_value[i] in self.mem_value and self.mem_value[self.mem_value[i]] != 'complex':
                self.mem_value[i] = self.mem_value[self.mem_value[i]]

    def constant_copy_propagation(self):
        self.set_mem_values()
        self.pb_changed = False
        for i in range(len(self.pb)):
            current_code = re.split(r',', self.pb[i].strip('()'))
            # assign
            if current_code[0] == 'ASSIGN' and re.match(r"\d+", current_code[1].strip()):
                if current_code[1] in self.mem_value and self.mem_value[current_code[1]] != 'complex':
                    self.useless_mem.append(current_code[1])
                    self.pb[i] = '(ASSIGN,' + self.mem_value[current_code[1]] + ',' + current_code[2] + ', )'
                    self.pb_changed = True
            # unconditional jump
            elif current_code[0] == 'JP' and re.match(r"@\d+", current_code[1].strip()):
                jmp_mem_addr = ' ' + current_code[1].strip(' @')
                if jmp_mem_addr in self.mem_value and re.match(r" #\d+", self.mem_value[jmp_mem_addr]):
                    self.useless_mem.append(jmp_mem_addr)
                    self.pb[i] = '(JP, ' + self.mem_value[jmp_mem_addr].strip(' #') + ', , )'
                    self.pb_changed = True
            # conditional jump
            elif current_code[0] == 'JPF' and re.match(r"@\d+", current_code[2].strip()):
                jmp_mem_addr = ' ' + current_code[2].strip(' @')
                if jmp_mem_addr in self.mem_value and re.match(r" #\d+", self.mem_value[jmp_mem_addr]):
                    self.useless_mem.append(jmp_mem_addr)
                    self.pb[i] = '(JPF,' + current_code[1] + ', ' + self.mem_value[jmp_mem_addr].strip(' #') + ', )'
                    self.pb_changed = True
            # arithmetic/logical ops
            elif current_code[0] in ['ADD', 'MULT', 'SUB', 'EQ', 'LT']:
                if current_code[1] in self.mem_value and self.mem_value[current_code[1]] != 'complex':
                    if current_code[2] in self.mem_value and self.mem_value[current_code[2]] != 'complex':
                        self.useless_mem.extend([current_code[1], current_code[2]])
                        self.pb[i] = '(' + current_code[0] + ',' + self.mem_value[current_code[1]] + ',' + \
                                     self.mem_value[current_code[2]] + ',' + current_code[3] + ')'
                        self.pb_changed = True
                    else:
                        self.useless_mem.append(current_code[1])
                        self.pb[i] = '(' + current_code[0] + ',' + self.mem_value[current_code[1]] + ',' + current_code[
                            2] + ',' + current_code[3] + ')'
                        self.pb_changed = True
                elif current_code[2] in self.mem_value and self.mem_value[current_code[2]] != 'complex':
                    self.useless_mem.append(current_code[2])
                    self.pb[i] = '(' + current_code[0] + ',' + current_code[1] + ',' + self.mem_value[
                        current_code[2]] + ',' + current_code[3] + ')'
                    self.pb_changed = True

    def constant_folding(self):
        for i in range(len(self.pb)):
            cc = re.split(r',', self.pb[i].strip('()'))  # cc :=  current_code
            if cc[0] == 'ADD' and re.match(r" #\d+", cc[1]) and re.match(r" #\d+", cc[2]):
                result = int(cc[1].strip(' #')) + int(cc[2].strip(' #'))
                self.pb[i] = '(ASSIGN, ' + str(result) + ',' + cc[3] + ', )'
                self.pb_changed = True
            elif cc[0] == 'SUB' and re.match(r" #\d+", cc[1]) and re.match(r" #\d+", cc[2]):
                result = int(cc[2].strip(' #')) - int(cc[1].strip(' #'))
                self.pb[i] = '(ASSIGN, ' + str(result) + ',' + cc[3] + ', )'
                self.pb_changed = True
            elif cc[0] == 'MULT' and re.match(r" #\d+", cc[1]) and re.match(r" #\d+", cc[2]):
                result = int(cc[1].strip(' #')) * int(cc[2].strip(' #'))
                self.pb[i] = '(ASSIGN, ' + str(result) + ',' + cc[3] + ', )'
                self.pb_changed = True
            elif cc[0] == 'EQ' and re.match(r" #\d+", cc[1]) and re.match(r" #\d+", cc[2]):
                result = ' #1,' if (int(cc[1].strip(' #')) == int(cc[2].strip(' #'))) else ' #0,'
                self.pb[i] = '(ASSIGN,' + result + cc[3] + ', )'
                self.pb_changed = True
            elif cc[0] == 'LT' and re.match(r" #\d+", cc[1]) and re.match(r" #\d+", cc[2]):
                result = ' #1,' if (int(cc[1].strip(' #')) < int(cc[2].strip(' #'))) else ' #0,'
                self.pb[i] = '(ASSIGN,' + result + cc[3] + ', )'
                self.pb_changed = True
            elif cc[0] == 'JPF' and cc[1] in self.mem_value and re.match(r' #\d+', self.mem_value[cc[1]]):
                if self.mem_value[cc[1]] == ' #0':
                    self.pb[i] = -1
                else:
                    self.pb[i] = '(JP,' + cc[2] + ', , )'
                self.pb_changed = True

    def delete_deadlines(self):
        indirect_addr = {0}
        new_addr = {}
        stack = []
        for i in range(len(self.code_gen_pb)):
            cc = re.split(r',', self.code_gen_pb[i].strip('()'))  # cc :=  current_code
            if cc[0] == 'ASSIGN' and cc[2] in self.useless_mem:
                self.pb[i] = '-1'
            elif cc[0] == 'JP' and re.match(r"@\d+", cc[1].strip()):
                indirect_addr.add(' ' + cc[1].strip(' @'))
            elif cc[0] == 'JPF' and re.match(r"@\d+", cc[2].strip()):
                indirect_addr.add(' ' + cc[2].strip(' @'))
        j = 0
        for i in range(len(self.code_gen_pb)):
            if self.pb[i] != '-1':
                new_addr[i] = j
                for item in stack:
                    new_addr[item] = j
                stack = []
                j += 1
            else:
                stack.append(i)
        if len(stack) != 0:
            for item in stack:
                new_addr[item] = j

        self.pb[:] = (value for value in self.pb if value != '-1')

        for i in range(len(self.pb)):
            cc = re.split(r',', self.pb[i].strip('()'))
            if cc[0] == 'JP' and re.match(r"\d+", cc[1].strip()):
                old_addr = int(cc[1].strip())
                self.pb[i] = '(' + cc[0] + ', ' + str(new_addr[old_addr]) + ', , )'
            elif cc[0] == 'JPF' and re.match(r"\d+", cc[2].strip()):
                old_addr = int(cc[2].strip())
                self.pb[i] = '(' + cc[0] + ',' + cc[1] + ', ' + str(new_addr[old_addr]) + ', )'
            elif cc[0] == 'ASSIGN' and cc[2] in indirect_addr and re.match(r' #\d+', cc[1]):
                old_addr = int(cc[1].strip(' #'))
                self.pb[i] = '(ASSIGN, #' + str(new_addr[old_addr]) + ',' + cc[2] + ', )'


def write_to_file(filepath, olist):
    with open(filepath, "w+") as f:
        for i in range(len(olist)):
            f.write(str(i) + '\t' + olist[i] + '\n')


def write_optimized_code(op_code):
    with open("optimized_output.txt", "w+") as f:
        for i in range(len(op_code.pb)):
            f.write(str(i) + '\t' + op_code.pb[i] + '\n')


if __name__ == '__main__':
    output = []
    with open("output.txt", 'r') as of:
        lines = of.readlines()
        for j in range(len(lines)):
            output.append(lines[j][:-1].split(maxsplit=1)[1])

    op = Optimizer(output)
    op.deep_optimization()
    write_optimized_code(op)

#   deep_optimization
#   simple_optimization
