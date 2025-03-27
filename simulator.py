registers=[0]*32
pc=[0]
pc_track=[]
def binary_convert(s):
    return int(s,2)-(1<<len(s))if s[0]=='1' else int(s,2)
opcodes={
    "0110011": "R",  
    "0010011": "I",  
    "0000011": "I",  
    "1100111": "I",  
    "0100011": "S",  
    "1100011": "B", 
    "1101111": "J", 
}
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
        #opcode+f3+f7
        a=self.instruction[-7:] + self.instruction[-15:-12] + self.instruction[-32:-25] 
        return self.operand.get(a)
    
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
        pc[0]=pc[0]+1
        print(4*pc[0]," ".join([str(x) for x in registers]))

class Itype:
    operand={"0000011010":"lw",
            "0010011000":"addi",
            "1100111000":"jalr"}

    def __init__(self,instruction):
        self.instruction=instruction
        self.imm=binary_convert(instruction[:12])
    
    def check(self):
        #opcode+f3+f7
        a=self.instruction[-7:] + self.instruction[-15:-12]
        return self.operand.get(a)
    
    def lw(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        registers[rd]=registers[rs1]+self.imm
       # print("immediate:",self.imm)
        pc[0]+=1
    
    def addi(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        registers[rd]=registers[rs1]+self.imm
        #print("immediate:",self.imm)
        pc[0]+=1

    def jalr(self):
        rd=int(self.instruction[-12:-7],2)
        rs1=int(self.instruction[-20:-15],2)
        registers[rd]=4*(pc[0]+1)
        pc[0]=(registers[rs1]+self.imm)//4
    
    def update(self,registers):
        a=self.check()
        #print(a)
        if(a=="lw"):
            self.lw()
        elif(a=="addi"):
            self.addi()
        elif(a=="jalr"):
            self.jalr()
    
    def output(self):
        self.update(registers)
        print(4*pc[0]," ".join([str(x) for x in registers]))


class Btype:
    operand={"1100011000":"beq",
            "1100011001":"bne",
            "1100011100":"blt"
            }

    def __init__(self,instruction):
        self.instruction=instruction
        self.imm=binary_convert(self.instruction[0]+self.instruction[-8]+self.instruction[1:7]+self.instruction[-12:-8])
    def check(self):
        a=self.instruction[-7:] + self.instruction[-15:-12]
        return self.operand.get(a)
    
    def bne(self):
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        if(registers[rs1]!=registers[rs2]):
            pc[0]=pc[0]+self.imm//4
        else:
            pc[0]+=1
    
    def beq(self):
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        if(rs1==0 and rs2==0 and self.imm==0):
            pc[0]+=1
        elif(registers[rs1]==registers[rs2]):
            pc[0]=pc[0]+self.imm//4 
        else:
            pc[0]+=1

    def blt(self):
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        if(registers[rs1]<registers[rs2]):
            pc[0]=pc[0]+self.imm//4
        else:
            pc[0]+=1
        
    
    def update(self,registers):
        a=self.check()
        if(a=="bne"):
            self.bne()
        elif(a=="blt"):
            self.blt()
        elif(a=="beq"):
            self.beq() 
    def output(self):
        self.update(registers)
        print(4*pc[0]," ".join([str(x) for x in registers]))

class Stype:
    def __init__(self,instruction):
        self.instruction=instruction
    def sw(self):
        imm=binary_convert(self.instruction[:7]+self.instruction[-12:-7])
        rs1=int(self.instruction[-20:-15],2)
        rs2=int(self.instruction[-25:-20],2)
        #print("register:",rs1," value:",registers[rs1],"register:",rs2," value:",registers[rs2],"immediate:",imm)
        registers[rs2]=registers[rs1]+imm
        pc[0]=pc[0]+1
    def output(self):
        self.sw()
        print(4*pc[0]," ".join([str(x) for x in registers]))

class Jtype:
    #only one instruction jal so no need to write unnecessary code
    def __init__(self,instruction):
        self.instruction=instruction
    def jal(self):
        rd=int(self.instruction[-12:-7],2)
        registers[rd]=4*(pc[0]+1)
        rearr=self.instruction[0]+self.instruction[12:20]+self.instruction[1:12]
        pc[0]=pc[0]+binary_convert(rearr)//4
    def output(self):
        self.jal()
        print(4*pc[0]," ".join([str(x) for x in registers]))
    
def input_process(filename):
    with open(filename,"r") as f:
        l=[x for x in f.read().split("\n") if x.strip()]
    return l

def identity(s):
    op=s[-7:]
    return opcodes.get(op)

f=input("enter file name:")
l=input_process(f)

while(pc[0]!=len(l)):
    #print(identity(l[pc[0]]))
    if(identity(l[pc[0]])=="R"):
        a=Rtype(l[pc[0]])
        a.output()
        
    elif(identity(l[pc[0]])=="J"):
        a=Jtype(l[pc[0]])
        a.output()
       
    elif(identity(l[pc[0]])=="S"):
        a=Stype(l[pc[0]])
        a.output()
    elif(identity(l[pc[0]])=="B"):
        a=Btype(l[pc[0]])
        a.output()
    elif(identity(l[pc[0]])=="I"):
        a=Itype(l[pc[0]])
        a.output()
    
    pc_track.append(pc[0]*4)
print(pc_track)
        

