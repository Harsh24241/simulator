registers = [0] * 32
pc = 4
opcode_type = {"0110011": "R", "0010011": "I", "1100011": "B"}

class Rtype:
    operand = {
        "01100110000000000": "add",
        "01100110000100000": "sub",
        "01100110100000000": "slt",
        "01100111010000000": "srl",
        "01100111100000000": "or",
        "01100111110000000": "and"
    }
    def __init__(self, instruction):
        self.instruction = instruction
    def check(self):
        key = self.instruction[-7:] + self.instruction[-15:-12] + self.instruction[-32:-25]
        return self.operand[key]
    def add(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        registers[rd] = registers[rs1] + registers[rs2]
    def sub(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        registers[rd] = registers[rs1] - registers[rs2]
    def slt(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        registers[rd] = 1 if registers[rs1] < registers[rs2] else 0
    def srl(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        registers[rd] = registers[rs1] >> registers[rs2]
    def or_isa(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        registers[rd] = registers[rs1] | registers[rs2]
    def and_isa(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        registers[rd] = registers[rs1] & registers[rs2]
    def update(self):
        op = self.check()
        if op == "add":
            self.add()
        elif op == "sub":
            self.sub()
        elif op == "slt":
            self.slt()
        elif op == "srl":
            self.srl()
        elif op == "or":
            self.or_isa()
        elif op == "and":
            self.and_isa()
    def output(self):
        self.update()
        print(" ".join(str(x) for x in registers))

class IType:
    operand = {"0010011000": "addi", "0010011011": "sltiu"}
    def __init__(self, instruction):
        self.instruction = instruction
    def check(self):
        key = self.instruction[-7:] + self.instruction[-15:-12]
        return self.operand.get(key)
    def addi(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        imm = int(self.instruction[-32:-20], 2)
        if self.instruction[-32] == '1':
            imm -= (1 << 12)
        registers[rd] = registers[rs1] + imm
    def sltiu(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        imm = int(self.instruction[-32:-20], 2)
        val_rs1 = registers[rs1] & 0xFFFFFFFF
        imm_u = imm & 0xFFFFFFFF
        registers[rd] = 1 if val_rs1 < imm_u else 0
    def update(self):
        op = self.check()
        if op == "addi":
            self.addi()
        elif op == "sltiu":
            self.sltiu()
    def output(self):
        self.update()
        print(" ".join(str(x) for x in registers))

class BType:
    operand = {"1100011000": "beq"}
    def __init__(self, instruction):
        self.instruction = instruction
    def check(self):
        key = self.instruction[-7:] + self.instruction[-15:-12]
        return self.operand.get(key)
    def beq(self):
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        imm_12 = self.instruction[0]
        imm_10_5 = self.instruction[1:7]
        imm_4_1 = self.instruction[20:24]
        imm_11 = self.instruction[24:25]
        imm_bin = imm_12 + imm_11 + imm_10_5 + imm_4_1
        imm = int(imm_bin, 2)
        if imm_bin[0] == '1':
            imm -= (1 << 12)
        global pc
        if registers[rs1] == registers[rs2]:
            pc = pc + imm
        else:
            pc = pc + 4
    def update(self):
        op = self.check()
        if op == "beq":
            self.beq()
    def output(self):
        self.update()
        print(" ".join(str(x) for x in registers))

def input_process(filename):
    with open(filename, "r") as f:
        return [line for line in f.read().split("\n") if line.strip()]

fname = input("enter file name:")
instructions = input_process(fname)
for inst in instructions:
    op = inst[-7:]
    if opcode_type.get(op) == "R":
        obj = Rtype(inst)
        print(pc, " ", end="")
        obj.output()
        pc += 4
    elif opcode_type.get(op) == "I":
        obj = IType(inst)
        print(pc, " ", end="")
        obj.output()
        pc += 4
    elif opcode_type.get(op) == "B":
        obj = BType(inst)
        print(pc, " ", end="")
        obj.output()
    print(registers)
