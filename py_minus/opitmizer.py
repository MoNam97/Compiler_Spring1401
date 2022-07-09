from py_minus.code_gen import CodeGenerator
import re
from typing import List
from dataclasses import dataclass


class Optimizer:
    code_gen = None
    pb = None
    code_blocks = []
    mem_value = []
    useless_mem = []

    def __init__(self, code_gen):
        self.code_gen = code_gen
        self.pb = code_gen.pb.copy()

    def copy_propagation(self):
        for i in range(len(self.code_gen.pb)):
            current_code = re.split(r',', self.code_gen.pb[i].strip('()'))
            if current_code[0] == 'ASSIGN' and re.match(r"\d+", current_code[1].strip()):
                self.mem_value.append((current_code[2], current_code[1]))
        #################################################################
        self.mem_value = []

    def constant_propagation(self):
        for i in range(len(self.code_gen.pb)):
            current_code = re.split(r',', self.code_gen.pb[i].strip('()'))
            if current_code[0] == 'ASSIGN' and re.match(r"#\d+", current_code[1].strip()):
                # print(self.code_gen.pb[i])
                self.mem_value.append((current_code[2], current_code[1]))

        for i in range(len(self.code_gen.pb)):
            current_code = re.split(r',', self.code_gen.pb[i].strip('()'))
            # assign
            if current_code[0] == 'ASSIGN' and re.match(r"\d+", current_code[1].strip()):
                temp = []
                for (t1, t2) in self.mem_value:
                    if t1 == current_code[1]:
                        temp.append(t2)
                if len(temp) == 1:
                    self.useless_mem.append(current_code[1])
                    self.pb[i] = '(ASSIGN,' + temp[0] + ',' + current_code[2] + ', )'
            # unconditional jump
            elif current_code[0] == 'JP' and re.match(r"@\d+", current_code[1].strip()):
                temp = []
                for (t1, t2) in self.mem_value:
                    if t1.strip() == current_code[1].strip(' @'):
                        temp.append(' ' + t2.strip(' #'))
                if len(temp) == 1:
                    self.useless_mem.append(' ' + current_code[1].strip(' @'))
                    self.pb[i] = '(JP,' + temp[0] + ', , )'
            # conditional jump
            elif current_code[0] == 'JPF' and re.match(r"@\d+", current_code[2].strip()):
                temp = []
                for (t1, t2) in self.mem_value:
                    if t1.strip() == current_code[2].strip(' @'):
                        temp.append(' ' + t2.strip(' #'))
                if len(temp) == 1:
                    self.useless_mem.append(' ' + current_code[2].strip(' @'))
                    self.pb[i] = '(JP,' + temp[0] + ', , )'
            # three address codes
            elif current_code[0] in ['ADD', 'MULT', 'SUB', 'EQ', 'LT']:
                tmp1, tmp2 = [], []
                for (t1, t2) in self.mem_value:
                    if t1 == current_code[1]:
                        tmp1.append(t2)
                    if t1 == current_code[2]:
                        tmp2.append(t2)
                if len(tmp1) == 1 and len(tmp2) == 1:
                    self.useless_mem.extend([current_code[1], current_code[2]])
                    self.pb[i] = '(' + current_code[0] + ',' + tmp1[0] + ',' + tmp2[0] + ',' + current_code[3] + ')'
                elif len(tmp1) == 1:
                    self.useless_mem.append(current_code[1])
                    self.pb[i] = '(' + current_code[0] + ',' + tmp1[0] + ',' + current_code[2] + ',' + current_code[3] + ')'
                elif len(tmp2) == 1:
                    self.useless_mem.append(current_code[2])
                    self.pb[i] = '(' + current_code[0] + ',' + current_code[1] + ',' + tmp2[0] + ',' + current_code[3] + ')'
        print(self.useless_mem)
        print(self.pb)

    def delete_deadlines(self):
        new_addr = {}
        stack = []
        for i in range(len(self.code_gen.pb)):
            current_code = re.split(r',', self.code_gen.pb[i].strip('()'))
            if current_code[0] == 'ASSIGN' and current_code[2] in self.useless_mem:
                self.pb[i] = '-1'
        j = 0
        for i in range(len(self.code_gen.pb)):
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
        print(self.pb)
