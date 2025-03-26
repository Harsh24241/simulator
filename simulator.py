registers = [0] * 32
pc = 4
memory = {}  # Simple memory for load/store operations

# Updated opcode type dictionary to cover all instruction types.
opcode_type = {
    "0110011": "R",  # R-type instructions (e.g., add, sub, etc.)
    "0010011": "I",  # I-type arithmetic (addi, sltiu)
    "0000011": "I",  # I-type load (lw)
    "1100111": "I",  # I-type jump register (jalr)
    "0100011": "S",  # S-type (store word: sw)
    "1100011": "B",  # B-type (branches, currently beq)
    "1101111": "J",  # J-type (jump: jal)
}

# --------- R-type Class (Register-Register Operations) ----------
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
        # key is built as: opcode + funct3 + funct7 (using specific bit slices)
        key = self.instruction[-7:] + self.instruction[-15:-12] + self.instruction[-32:-25]
        return self.operand.get(key, "unknown")
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

# --------- I-type Class (Immediate and Load/Jump Register Instructions) ----------
class IType:
    # This dictionary maps the concatenated (opcode + funct3) to the operation name.
    operand = {
        "0010011000": "addi",
        "0010011011": "sltiu",
        "0000011010": "lw",
        "1100111000": "jalr"
    }
    def __init__(self, instruction):
        self.instruction = instruction
    def check(self):
        key = self.instruction[-7:] + self.instruction[-15:-12]
        return self.operand.get(key, "unknown")
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
    def lw(self):
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        imm = int(self.instruction[-32:-20], 2)
        if self.instruction[-32] == '1':
            imm -= (1 << 12)
        address = registers[rs1] + imm
        registers[rd] = memory.get(address, 0)
    def jalr(self):
        global pc
        rd = int(self.instruction[-12:-7], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        imm = int(self.instruction[-32:-20], 2)
        if self.instruction[-32] == '1':
            imm -= (1 << 12)
        temp = pc + 4
        pc = (registers[rs1] + imm) & ~1  # Clear the LSB
        registers[rd] = temp
    def update(self):
        op = self.check()
        if op == "addi":
            self.addi()
        elif op == "sltiu":
            self.sltiu()
        elif op == "lw":
            self.lw()
        elif op == "jalr":
            self.jalr()
    def output(self):
        self.update()
        print(" ".join(str(x) for x in registers))

# --------- S-type Class (Store Instructions) ----------
class SType:
    operand = {
        "0100011010": "sw"
    }
    def __init__(self, instruction):
        self.instruction = instruction
    def check(self):
        key = self.instruction[-7:] + self.instruction[-15:-12]
        return self.operand.get(key, "unknown")
    def sw(self):
        # In S-type instructions the immediate is split between two parts.
        # For simplicity here we concatenate the two slices.
        rs2 = int(self.instruction[-25:-20], 2)
        rs1 = int(self.instruction[-20:-15], 2)
        # Combine imm bits from different positions
        imm_bin = self.instruction[-32:-25] + self.instruction[-15:-12]
        imm = int(imm_bin, 2)
        if self.instruction[-32] == '1':
            imm -= (1 << len(imm_bin))
        address = registers[rs1] + imm
        memory[address] = registers[rs2]
    def update(self):
        op = self.check()
        if op == "sw":
            self.sw()
    def output(self):
        self.update()
        print(" ".join(str(x) for x in registers))

# --------- B-type Class (Branch Instructions) ----------
class BType:
    operand = {
        "1100011000": "beq",
        # You could add "bne", "blt", etc. with additional keys here.
    }
    def __init__(self, instruction):
        self.instruction = instruction
    def check(self):
        key = self.instruction[-7:] + self.instruction[-15:-12]
        return self.operand.get(key, "unknown")
    def beq(self):
        rs1 = int(self.instruction[-20:-15], 2)
        rs2 = int(self.instruction[-25:-20], 2)
        # Reconstructing the immediate from its parts
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

# --------- J-type Class (Jump Instructions) ----------
class JType:
    operand = {
        "1101111": "jal"
    }
    def __init__(self, instruction):
        self.instruction = instruction
    def jal(self):
        global pc
        rd = int(self.instruction[-12:-7], 2)
        # The J-type immediate is split among several fields.
        imm_20 = self.instruction[0]
        imm_10_1 = self.instruction[10:20]
        imm_11 = self.instruction[9:10]
        imm_19_12 = self.instruction[1:9]
        imm_bin = imm_20 + imm_19_12 + imm_11 + imm_10_1
        imm = int(imm_bin, 2)
        if imm_bin[0] == '1':
            imm -= (1 << 20)
        registers[rd] = pc + 4
        pc = pc + imm
    def update(self):
        # Only one instruction (jal) is supported for J-type.
        self.jal()
    def output(self):
        self.update()
        print(" ".join(str(x) for x in registers))

# --------- Helper Function to Process Input File ----------
def input_process(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f.read().split("\n") if line.strip()]

# --------- Main Loop for Processing Instructions ----------
fname = input("enter file name:")
instructions = input_process(fname)
for inst in instructions:
    op = inst[-7:]
    inst_type = opcode_type.get(op)
    print("PC:", pc, "Instruction type:", inst_type)
    if inst_type == "R":
        obj = Rtype(inst)
        obj.output()
        pc += 4
    elif inst_type == "I":
        obj = IType(inst)
        obj.output()
        pc += 4
    elif inst_type == "S":
        obj = SType(inst)
        obj.output()
        pc += 4
    elif inst_type == "B":
        obj = BType(inst)
        obj.output()
    elif inst_type == "J":
        obj = JType(inst)
        obj.output()
    print("Registers:", registers)
