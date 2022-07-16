import re


class SBlock:
    in_from = []
    first = None
    last = None
    out_to = []

    def __init__(self, fint):
        self.first = fint


class Optimizer:
    code_gen_pb = None
    pb = None
    code_blocks = []
    mem_value = {}
    useless_mem = []

    sblocks = {}

    def __init__(self, pb):
        self.code_gen_pb = pb
        self.pb = pb.copy()

    def optimize_code(self):
        self.constant_copy_propagation()
        self.delete_deadlines()

    def set_mem_values(self):
        self.mem_value = {}
        for i in range(len(self.code_gen_pb)):
            current_code = re.split(r',', self.code_gen_pb[i].strip('()'))
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
                self.mem_value[' '+current_code[3].strip(' @')] = 'complex'

        for i in self.mem_value:
            if self.mem_value[i] in self.mem_value and self.mem_value[self.mem_value[i]] != 'complex':
                self.mem_value[i] = self.mem_value[self.mem_value[i]]

        print(self.mem_value)
        for i in self.mem_value:
            if self.mem_value[i] != 'complex':
                print(i)

    def constant_copy_propagation(self):
        self.set_mem_values()

        for i in range(len(self.code_gen_pb)):
            current_code = re.split(r',', self.code_gen_pb[i].strip('()'))
            # assign
            if current_code[0] == 'ASSIGN' and re.match(r"\d+", current_code[1].strip()):
                if current_code[1] in self.mem_value and self.mem_value[current_code[1]] != 'complex':
                    self.useless_mem.append(current_code[1])
                    self.pb[i] = '(ASSIGN,' + self.mem_value[current_code[1]] + ',' + current_code[2] + ', )'
            # unconditional jump
            elif current_code[0] == 'JP' and re.match(r"@\d+", current_code[1].strip()):
                jmp_mem_addr = ' ' + current_code[1].strip(' @')
                if jmp_mem_addr in self.mem_value and re.match(r" #\d+", self.mem_value[jmp_mem_addr]):
                    self.useless_mem.append(jmp_mem_addr)
                    self.pb[i] = '(JP, ' + self.mem_value[jmp_mem_addr].strip(' #') + ', , )'
            # conditional jump
            elif current_code[0] == 'JPF' and re.match(r"@\d+", current_code[2].strip()):
                jmp_mem_addr = ' ' + current_code[2].strip(' @')
                if jmp_mem_addr in self.mem_value and re.match(r" #\d+", self.mem_value[jmp_mem_addr]):
                    self.useless_mem.append(jmp_mem_addr)
                    self.pb[i] = '(JPF,' + current_code[1] + ', ' + self.mem_value[jmp_mem_addr].strip(' #') + ', )'
            # arithmetic/logical ops
            elif current_code[0] in ['ADD', 'MULT', 'SUB', 'EQ', 'LT']:
                if current_code[1] in self.mem_value and self.mem_value[current_code[1]] != 'complex':
                    if current_code[2] in self.mem_value and self.mem_value[current_code[2]] != 'complex':
                        self.useless_mem.extend([current_code[1], current_code[2]])
                        self.pb[i] = '(' + current_code[0] + ',' + self.mem_value[current_code[1]] + ',' + \
                                     self.mem_value[current_code[2]] + ',' + current_code[3] + ')'
                    else:
                        self.useless_mem.append(current_code[1])
                        self.pb[i] = '(' + current_code[0] + ',' + self.mem_value[current_code[1]] + ',' + current_code[
                            2] + ',' + current_code[3] + ')'
                elif current_code[2] in self.mem_value and self.mem_value[current_code[2]] != 'complex':
                    self.useless_mem.append(current_code[2])
                    self.pb[i] = '(' + current_code[0] + ',' + current_code[1] + ',' + self.mem_value[
                        current_code[2]] + ',' + current_code[3] + ')'

    def constant_folding(self):
        for i in range(len(self.code_gen_pb)):
            current_code = re.split(r',', self.code_gen_pb[i].strip('()'))

    def delete_deadlines(self):
        indirect_addr = {0}
        new_addr = {}
        stack = []
        for i in range(len(self.code_gen_pb)):
            current_code = re.split(r',', self.code_gen_pb[i].strip('()'))
            if current_code[0] == 'ASSIGN' and current_code[2] in self.useless_mem:
                self.pb[i] = '-1'
            elif current_code[0] == 'JP' and re.match(r"@\d+", current_code[1].strip()):
                indirect_addr.add(' '+current_code[1].strip(' @'))
            elif current_code[0] == 'JPF' and re.match(r"@\d+", current_code[2].strip()):
                indirect_addr.add(' '+current_code[2].strip(' @'))
        write_to_file('before_delete.txt', self.pb)
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
            current_code = re.split(r',', self.pb[i].strip('()'))
            if current_code[0] == 'JP' and re.match(r"\d+", current_code[1].strip()):
                old_addr = int(current_code[1].strip())
                self.pb[i] = '(' + current_code[0] + ', ' + str(new_addr[old_addr]) + ', , )'
            elif current_code[0] == 'JPF' and re.match(r"\d+", current_code[2].strip()):
                old_addr = int(current_code[2].strip())
                self.pb[i] = '(' + current_code[0] + ',' + current_code[1] + ', ' + str(new_addr[old_addr]) + ', )'
            elif current_code[0] == 'ASSIGN' and current_code[2] in indirect_addr:
                old_addr = int(current_code[1].strip(' #'))
                self.pb[i] = '(ASSIGN, #' + str(new_addr[old_addr]) + ',' + current_code[2] + ', )'

    def temp_blocks(self, dest, i, cur_block):
        if dest in self.sblocks.keys():
            self.sblocks[dest].in_from.append(cur_block)
            cur_block.out_to.append(self.sblocks[dest])
            cur_block.last = i
        else:
            temp = SBlock(dest)
            temp.in_from.append(cur_block)
            self.sblocks[dest] = temp

            cur_block.out_to.append(temp)
            cur_block.last = i

        if i < len(self.pb) - 1:
            temp = SBlock(i + 1)
            temp.in_from.append(cur_block)
            self.sblocks[i + 1] = temp
            cur_block.out_to.append(temp)
            cur_block = temp
        return cur_block

    def simple_block_detector(self):
        if self.pb is None:
            print('Error! program block not initialized.')
        else:
            cur_block = SBlock(0)
            cur_block.in_from.append(-1)
            self.sblocks[0] = cur_block
            for i in range(len(self.pb)):
                current_code = re.split(r',', self.pb[i].strip('()'))
                if current_code[0] == 'JP':
                    if re.match(r"\d+", current_code[1].strip()):
                        dest = int(current_code[1].strip())
                        cur_block = self.temp_blocks(dest, i, cur_block)
                    else:
                        print(i, self.pb[i])

                elif current_code[0] == 'JPF':
                    if re.match(r"\d+", current_code[2].strip()):
                        dest = int(current_code[2].strip())
                        cur_block = self.temp_blocks(dest, i, cur_block)
                    else:
                        print(i, self.pb[i])

                if i == len(self.pb):
                    cur_block.out_to.append(-1)

            tmpL = []
            for item in self.sblocks:
                # print(item, self.sblocks[item].first, self.sblocks[item].last)
                # if self.sblocks[item] is not None:
                tmpL.append((self.sblocks[item].first, self.sblocks[item].last))
            tmpL.sort()
            for i in tmpL:
                print(i)


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
    op.optimize_code()
    # op.simple_block_detector()
    write_optimized_code(op)
