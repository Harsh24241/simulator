registers=[0]*32
pc=4
opcodes={"0110011":"R"}
class Rtype:
    isa={"opcode":[0,6], "f7":[25,31] , "s1":[7,11] , "s2":[15,19] , "s3" :[20,24] , "f3":[12,14]}
    operand={"01100110000000000":"add",
            "01100110000100000":"sub",
            "01100110100000000":"slt",
            "01100111010000000":"srl",
            "01100111100000000":"or",
            "01100111110000000":"and"}

    def __init__(self,instruction):
        self.instruction=instruction
    
    def check(self):
        a=self.instruction[-7:] + self.instruction[-15:-12] + self.instruction[-32:-25] 
        return self.operand[a]
    
    def add(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        registers[rd]=registers[rs1]+registers[rs2]
    
    def sub(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        registers[rd]=registers[rs1]-registers[rs2]

    def slt(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        if(registers[rs1]<registers[rs2]):
            registers[rd]=1
        
    def srl(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        registers[rd]=registers[rs1]>>registers[rs2]

    def or_isa(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        registers[rd]=registers[rs1] | registers[rs2]

    def and_isa(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        registers[rd]=registers[rs1] & registers[rs2]
    
    
    def update(self,registers):
        a=self.check()
        if(a=="add"):
            self.add()
        elif(a=="sub"):
            self.sub()
        elif(a=="slt"):
            self.slt()
        elif(a=="srl"):
            self.srl()
        elif(a=="or"):
            self.or_isa()
        elif(a=="and"):
            self.and_isa()
    
    def output(self):
        self.update(registers)
        print(" ".join([str(x) for x in registers]))
    

def input_process(filename):
    with open(filename,"r") as f:
        l=[x for x in f.read().split("\n") if x.strip()]
    return l

def identity(s):
    op=s[-7:]
    return opcodes.get(op)

f=input("enter file name:")
l=input_process(f)

for i in range(len(l)):
    #print(identity(l[i]))
    if(identity(l[i])=="R"):
        l[i]=Rtype(l[i])
        print(pc," ",end="")
        l[i].output()
        pc+=4
    print(registers)

