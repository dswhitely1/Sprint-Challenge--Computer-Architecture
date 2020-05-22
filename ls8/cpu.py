"""CPU functionality."""
import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
SP_MEM = 0xf3
CALL = 0b01010000
RET = 0b00010001
SP = 7
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0x00
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = SP_MEM
        self.instruction = {LDI: self.ldi, PRN: self.prn, MUL: self.mul, HLT: self.hlt, POP: self.pop, PUSH: self.push,
                            CALL: self.call, RET: self.ret, ADD: self.add, CMP: self.cmp, JMP: self.jmp}
        self.flag = 0b0000000

    def load(self):
        """Load a program into memory."""
        program = []
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    string_val = line.split('#')[0].strip()
                    if string_val == '':
                        continue
                    v = int(string_val, 2)
                    program = program + [v]
        except FileNotFoundError:
            print('File Not Found')
            exit(1)
        except IndexError:
            print('You need to specify the file to run.')
            exit(1)

        address = 0

        # For now, we've just hardcoded a program:

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = bin(1)
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = bin(1 << 2)
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = bin(1 << 1)

        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def get_arg_count(self, value, comparision=0b11000000):
        x = value & comparision
        x = x >> 6
        return x

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def ldi(self):
        address = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.reg[address] = value
        count = self.get_arg_count(LDI)
        self.pc += count + 1

    def prn(self):
        address = self.ram[self.pc + 1]
        print(self.reg[address])
        count = self.get_arg_count(PRN)
        self.pc += count + 1

    def mul(self):
        self.alu('MUL', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += self.get_arg_count(MUL) + 1

    def hlt(self):
        exit(0)

    def call(self):
        return_addr = self.pc + 2
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], return_addr)
        reg_num = self.ram_read(self.pc + 1)
        subroutine_add = self.reg[reg_num]
        self.pc = subroutine_add

    def ret(self):
        return_addr = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        self.pc = return_addr

    def cmp(self):
        self.alu('CMP', self.reg[self.pc + 1], self.reg[self.pc + 2])
        self.pc = self.get_arg_count(CMP)

    def jmp(self):
        self.pc = self.reg[self.pc + 1]

    def jeq(self):
        value = self.flag & 0b00000001
        if value == 0b00000001:
            self.pc = self.reg[self.pc + 1]
        else:
            self.pc = self.get_arg_count(JEQ) + 1

    def jne(self):
        value = self.flag & 0b00000001
        if value == 0b00000000:
            self.pc = self.reg[self.pc + 1]
        else:
            self.pc = self.get_arg_count(JNE) + 1

    def push(self):
        self.reg[SP] -= 1
        address = self.ram_read(self.pc + 1)
        self.ram_write(self.reg[SP], self.reg[address])
        self.pc += self.get_arg_count(PUSH) + 1

    def pop(self):
        address = self.ram[self.pc + 1]
        self.reg[address] = self.ram_read(self.reg[SP])
        self.pc += self.get_arg_count(POP) + 1
        self.reg[SP] += 1

    def add(self):
        self.alu('ADD', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += self.get_arg_count(MUL) + 1

    def run(self):
        """Run the CPU."""
        run = True
        while run:
            # print(self.ram[self.pc])
            self.instruction[self.ram[self.pc]]()
