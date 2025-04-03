import sys

registers=[0]*32
registers[2]=380
pc=[0]
trace=[]
memory={
"0x00010000":0,
"0x00010004":0,
"0x00010008":0,
"0x0001000C":0,
"0x00010010":0,
"0x00010014":0,
"0x00010018":0,
"0x0001001C":0,
"0x00010020":0,
"0x00010024":0,
"0x00010028":0,
"0x0001002C":0,
"0x00010030":0,
"0x00010034":0,
"0x00010038":0,
"0x0001003C":0,
"0x00010040":0,
"0x00010044":0,
"0x00010048":0,
"0x0001004C":0,
"0x00010050":0,
"0x00010054":0,
"0x00010058":0,
"0x0001005C":0,
"0x00010060":0,
"0x00010064":0,
"0x00010068":0,
"0x0001006C":0,
"0x00010070":0,
"0x00010074":0,
"0x00010078":0,
"0x0001007C":0
}



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
def negto():
    for i in range(0,32):
        if registers[i]<0:
            bin_32=format(registers[i] & 0xFFFFFFFF,'032b')
            registers[i]=int(bin_32,2)











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
        a=self.instruction[25:32] + self.instruction[17:20] + self.instruction[:7] 
        return self.operand.get(a)
    
    def add(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        registers[rd]=registers[rs1]+registers[rs2]
    
    def sub(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        registers[rd]=registers[rs1]-registers[rs2]

    def slt(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        if(registers[rs1]<registers[rs2]):
            registers[rd]=1
        
    def srl(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        registers[rd]=registers[rs1]>>registers[rs2]

    def or_isa(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        registers[rd]=registers[rs1] | registers[rs2]

    def and_isa(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
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
        pc[0]+=4
        registers[0]=0
        negto()
        trace.append(str(pc[0])+" "+" ".join([str(x) for x in registers]))
       



class Itype:
    operand={"0000011":"lw",
            "0010011":"addi",
            "1100111":"jalr"}

    def __init__(self,instruction):
        self.instruction=instruction
        self.imm=binary_convert(instruction[:12])
        self.imm_jalr=binary_convert(instruction[:11]+'0')
        
    
    def check(self):
        #opcode+f3+f7
        a=self.instruction[25:32]
        return self.operand.get(a)
    
    def lw(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        a=format(registers[rs1]+self.imm,"#010x")
        #if a in memory:
        registers[rd]=memory[a]
        pc[0]+=4
       
    
    def addi(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        registers[rd]=registers[rs1]+self.imm
        pc[0]+=4
        
        

    def jalr(self):
        rd=int(self.instruction[20:25],2)
        rs1=int(self.instruction[12:17],2)
        registers[rd]=4+pc[0]
        #print("index:",i)
        #print("pc",pc[0],"rs1",rs1)
        pc[0]=registers[rs1]+self.imm_jalr
        #print("pc",pc[0],"immediate for jalr:",self.imm_jalr,"immediate for all:",self.imm)
    
    def update(self,registers):
        a=self.check()
        #print("hi")
        if(a=="lw"):
            self.lw()
        elif(a=="addi"):
            self.addi()
        elif(a=="jalr"):
            self.jalr()
    
    def output(self):
        self.update(registers)
        negto()
        registers[0]=0
        #print("immediate :",self.imm,"at index:",i)
        trace.append(str(pc[0])+" "+" ".join([str(x) for x in registers]))
        #print("trace:",trace[i])
       
       





class Btype:
    operand={"1100011000":"beq",
            "1100011001":"bne",
            "1100011100":"blt"
            }

    def __init__(self,instruction):
        self.instruction=instruction
        self.imm=self.instruction[0]+self.instruction[24]+self.instruction[1:7]+self.instruction[20:24]
        #self.imm=instruction>>20
        #print("value of immediate:",2*binary_convert(self.imm),"instruction index:",i)
    def check(self):
        a=self.instruction[25:32] + self.instruction[17:20]
        return self.operand.get(a)
    
    def bne(self):
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        if(registers[rs1]!=registers[rs2]):
           #pc[0]+=binary_convert(self.imm[:-1]+'0')
           pc[0]+=binary_convert(self.imm)<<1
        else:
            pc[0]+=4
    
    def beq(self):
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        if(rs1==0 and rs2==0 and binary_convert(self.imm)==0):
           #pc[0]=len(l)*4
           pc[0]+=4
        elif(registers[rs1]==registers[rs2]):
           pc[0]+=binary_convert(self.imm)<<1

        else:
           pc[0]+=4

    # def blt(self):
    #     rs1=int(self.instruction[12:17],2)
    #     rs2=int(self.instruction[7:12],2)
    #     if(registers[rs1]<registers[rs2]):
    #         pass
    #     else:
    #         pass
        
    
    def update(self,registers):
        a=self.check()
        if(a=="bne"):
            self.bne()
        # elif(a=="blt"):
        #     self.blt()
        elif(a=="beq"):
            self.beq() 
    def output(self):
        self.update(registers)
        registers[0]=0
        negto()
        trace.append(str(pc[0])+" "+" ".join([str(x) for x in registers]))
        





class Stype:
    def __init__(self,instruction):
        self.instruction=instruction
    def sw(self):
        imm=binary_convert(self.instruction[:7]+self.instruction[20:25])
        rs1=int(self.instruction[12:17],2)
        rs2=int(self.instruction[7:12],2)
        a=format(registers[rs1]+imm,"#010x")
        #print("instruction",i,"pc",pc[0],"memory address",a)
        #if a in memory:
        memory[a]=registers[rs2]
        pc[0]+=4
        
        trace.append(str(pc[0])+" "+" ".join([str(x) for x in registers]))
       
        
    def output(self):
        self.sw()
        registers[0]=0
        negto()
    
        


class Jtype:
   
    def __init__(self,instruction):
        self.instruction=instruction
    def jal(self):
        rd=int(self.instruction[20:25],2)
        registers[rd]=4+pc[0]
        rearr=self.instruction[0]+self.instruction[12:20]+self.instruction[11]+self.instruction[1:11]
        pc[0]+=binary_convert(rearr[:-1]+'0')<<1
      
    def output(self):
        self.jal()
        registers[0]=0
        negto()
        trace.append(str(pc[0])+" "+" ".join([str(x) for x in registers]))
       
        
        




def input_process(filename):
    with open(filename,"r") as f:
        l=[x for x in f.read().split("\n") if x.strip()]
    return l




def identity(s):
    op=s[25:32]
    return opcodes.get(op)

# f=input("enter filename:")
f=sys.argv[1]
output_file=sys.argv[2]
l=input_process(f)




i=0
limit=0
while pc[0]<4*(len(l)-1) and limit<100:
   
    if(identity(l[i])=="R"):
        a=Rtype(l[i])
        a.output()
        
    elif(identity(l[i])=="J"):
        a=Jtype(l[i])
        a.output()
       
    elif(identity(l[i])=="S"):
        a=Stype(l[i])
        a.output()
    elif(identity(l[i])=="B"):
        a=Btype(l[i])
        a.output()
    elif(identity(l[i])=="I"):
        a=Itype(l[i])
        a.output()
    i=pc[0]//4
    limit+=1
trace.append(trace[-1])

for i in range(len(trace)):
    trace[i]=" ".join(["0b"+format(int(x) & 0xFFFFFFFF,'032b') for x in trace[i].split()])

for i in memory:
    memory[i]="0b"+format(memory[i] & 0xFFFFFFFF,'032b')

with open(output_file,'w') as file:
    for item in trace:
        file.write(item+'\n')
    for item in memory:
        file.write(item+":"+memory[item]+'\n')

# for i in trace:
#     print(i)
# for i in memory:
#     print(i,":",memory[i])