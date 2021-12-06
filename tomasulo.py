from collections import deque
from typing import Deque, List, TextIO
import sys

ARITMETICA : List[str] = ["ADD", "ADDI", "SUB", "SUBI", "MUL", "DIV"]
LOGICA : List[str] = ["AND", "OR", "NOT"]
DESVIO : List[str] = ["BLT", "BGT", "BEQ","BNE", "J"]
MEMORIA : List[str] = ["LW", "SW"]
outputFile = open("output.txt", "w")

class ReservationStation:
    def __init__(self) -> None:
        self.busy = False
        self.exec = None
        self.op = None
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.A = None

class Register:
    def __init__(self) -> None:
        self.Qi = None
        self.value = 0

class DataMemory:
    def __init__(self) -> None: 
        self.Qi = None
        self.value = 0 # TODO: rever atributos depois

class FunctionalUnit:
    def __init__(self) -> None:
        self.busy = False
        self.inst = None

class Tomasulo:
    def __init__(self, instList : List[List[str]]) -> None:    
        self.pc : int = 0
        self.clock : int = 0
        self.instrucoes : int = 0
        self.rsAddI : int = 0
        self.rsMulI : int = 16
        self.rsLdI : int = 32
        self.instList : List[List[str]] = instList
        self.filaDespacho : Deque[List[str]] = deque()
        self.addUnit : FunctionalUnit = [FunctionalUnit() for i in range(3)]
        self.mulUnit : FunctionalUnit = [FunctionalUnit() for i in range(3)]
        self.ldUnit : FunctionalUnit = [FunctionalUnit() for i in range(3)]
        self.memory : DataMemory = [DataMemory() for i in range(512)]
        self.registerStat : Register = [Register() for i in range(32)]
        self.RS : ReservationStation = [ReservationStation() for i in range(48)]
        # 48 estações de reserva sendo:
        # 0 - 15 : add e sub
        # 16 - 31 : mult e div
        # 32 - 47 : ld e st
        # como vão ser feitas as operações de desvio e logicas?

    # Realiza a busca da instrução na queue
    def search(self) -> None:
        if self.pc >= len(self.instList):
            return None
        if len(self.filaDespacho) < 16:
            self.filaDespacho.append(self.instList[self.pc])
            self.pc += 1

    # Faz o despacho da instrução
    def issue(self) -> None:
        if len(self.filaDespacho) < 1:
            return
        inst = self.filaDespacho.popleft()
        op = inst[0]
        r = 0
        if op in ARITMETICA or op in LOGICA:
            if op == "MUL" or op == "DIV":
                r = 16
                while self.RS[r].busy and r < 32:
                    r += 1
            else:
                while self.RS[r].busy and r < 16:
                    r += 1
            if op == "ADDI" or op == "SUBI":
                try:
                    rd = int(inst[1][1:])
                    rs = int(inst[2][1:])
                    imm = int(inst[3])
                except:
                    raise Exception("Sintaxe invalida")
                    
                if self.registerStat[rs].Qi != None:
                    self.RS[r].Qj = self.registerStat[rs].Qi
                else:
                    self.RS[r].Vj = self.registerStat[rs].value
                    
                self.RS[r].Vk = 0
                self.RS[r].A = imm
            else:
                try:
                    rd = int(inst[1][1:])
                    rs = int(inst[2][1:])
                    rt = int(inst[3][1:])
                except:
                    raise Exception("Sintaxe invalida")
                if self.registerStat[rs].Qi != None:
                    self.RS[r].Qj = self.registerStat[rs].Qi
                else:
                    self.RS[r].Vj = self.registerStat[rs].value
                    #self.RS[r].Qj = 0
                
                if self.registerStat[rt].Qi != None:
                    self.RS[r].Qk = self.registerStat[rt].Qi
                else:
                    self.RS[r].Vk = self.registerStat[rt].value
                    #self.RS[r].Qk = 0
            
            self.RS[r].busy = True
            self.registerStat[rd].Qi = r
        elif op in DESVIO:
            while self.RS[r].busy and r < 16:
                r += 1
            if op == "J":
                try:
                    imm = int(inst[1])
                except:
                    raise Exception("Sintaxe invalida")
                self.RS[r].Vj = 0
                self.RS[r].Vk = 0
            else:
                try:
                    rs = int(inst[1][1:])
                    rt = int(inst[2][1:])
                    imm = int(inst[3])
                except:
                    raise Exception("Sintaxe invalida")
                if self.registerStat[rs].Qi != None:
                    self.RS[r].Qj = self.registerStat[rs].Qi
                else:
                    self.RS[r].Vj = self.registerStat[rs].value
                
                if self.registerStat[rt].Qi != None:
                    self.RS[r].Qk = self.registerStat[rt].Qi
                else:
                    self.RS[r].Vk = self.registerStat[rt].value
            self.RS[r].A = imm
            self.RS[r].busy = True
        elif op in MEMORIA:
            rd = int(inst[1][1:])
            imm, rs = inst[2].replace("(", " ").replace(")", " ").split()
            imm = int(imm)
            rs = int(rs[1:])
            r = 32
            while self.RS[r].busy and r < 48:
                r += 1
            if op == "LW":
                """
                if self.registerStat[rs].Qi != 0:
                    self.RS[r].Qj = self.registerStat[rs].Qi
                else:
                    self.RS[r].Vj = self.registerStat[rs].value
                    self.RS[r].Qj = 0
                """
                self.RS[r].Vj = self.memory[rs].value
                self.RS[r].A = imm
                self.RS[r].busy = True
                self.registerStat[rd].Qi = r
            elif op == "SW":
                """
                if self.registerStat[rs].Qi != 0:
                    self.RS[r].Qj = self.registerStat[rs].Qi
                else:
                    self.RS[r].Vj = self.registerStat[rs].value
                    self.RS[r].Qj = 0
                """
                self.RS[r].Vj = self.registerStat[rs].value
                self.RS[r].A = imm
                self.RS[r].busy = True
                self.memory[rd].Qi = r
        else:
            print(op) # TODO : remove
            raise Exception("Instrução não reconhecida")
        self.RS[r].exec = -1
        self.RS[r].op = op
        self.instrucoes += 1

    # Executa as instruções
    def setUnits(self): 
        for unit in self.addUnit:
            if unit.busy:
                self.RS[unit.inst].exec -= 1
        for unit in self.mulUnit:
            if unit.busy:
                self.RS[unit.inst].exec -= 1
        for unit in self.ldUnit:
            if unit.busy:
                self.RS[unit.inst].exec -= 1
        
        # Enviar instruções para as unidades funcionais
        for i in range(16):
            if self.RS[self.rsAddI].busy and self.RS[self.rsAddI].exec == -1 and self.RS[self.rsAddI].Vj != None and self.RS[self.rsAddI].Vk != None:
                if not self.addUnit[0].busy:
                    self.addUnit[0].inst = self.rsAddI
                    self.addUnit[0].busy = True
                elif not self.addUnit[1].busy:
                    self.addUnit[1].inst = self.rsAddI
                    self.addUnit[1].busy = True
                elif not self.addUnit[2].busy:
                    self.addUnit[2].inst = self.rsAddI
                    self.addUnit[2].busy = True
                else:
                    break
                # setar o clock da operação todas levam 5 de clock para serem concluidas
                self.RS[self.rsAddI].exec = 5
            self.rsAddI = (self.rsAddI + 1) % 16
        for i in range(16):
            if self.RS[self.rsMulI].busy and self.RS[self.rsMulI].exec == -1 and self.RS[self.rsMulI].Vj != None and self.RS[self.rsMulI].Vk != None:
                if not self.mulUnit[0].busy:
                    self.mulUnit[0].inst = self.rsMulI
                    self.mulUnit[0].busy = True
                elif not self.addUnit[1].busy:
                    self.mulUnit[1].inst = self.rsMulI
                    self.mulUnit[1].busy = True
                elif not self.addUnit[2].busy:
                    self.mulUnit[2].inst = self.rsMulI
                    self.mulUnit[2].busy = True
                else:
                    break
                # setar o clock da operação
                if self.RS[self.rsMulI].op == "MUL":
                    self.RS[self.rsMulI].exec = 15
                else:
                    self.RS[self.rsMulI].exec = 25
            self.rsMulI = ((self.rsMulI + 1) % 16) + 16
        for i in range(16):
            if self.RS[self.rsLdI].busy and self.RS[self.rsLdI].exec == -1:
                if not self.ldUnit[0].busy:
                    self.ldUnit[0].inst = self.rsLdI
                    self.ldUnit[0].busy = True
                elif not self.ldUnit[1].busy:
                    self.ldUnit[1].inst = self.rsLdI
                    self.ldUnit[1].busy = True
                elif not self.ldUnit[2].busy:
                    self.ldUnit[2].inst = self.rsLdI
                    self.ldUnit[2].busy = True
                else:
                    break
                # setar o clock da operação todas levam 5 de clock para serem concluidas
                self.RS[self.rsLdI].exec = 5
            self.rsLdI = ((self.rsLdI + 1) % 16) + 32

    def execute(self, inst : int):
        if self.RS[inst].op == "ADD":
            return self.RS[inst].Vj + self.RS[inst].Vk
        elif self.RS[inst].op == "SUB":
            return self.RS[inst].Vj - self.RS[inst].Vk
        elif self.RS[inst].op == "ADDI":
            return self.RS[inst].Vj + self.RS[inst].A
        elif self.RS[inst].op == "SUBI":
            return self.RS[inst].Vj - self.RS[inst].A
        elif self.RS[inst].op == "MUL":
            return self.RS[inst].Vj * self.RS[inst].Vk
        elif self.RS[inst].op == "DIV":
            return self.RS[inst].Vj // self.RS[inst].Vk
        elif self.RS[inst].op == "AND":
            return self.RS[inst].Vj & self.RS[inst].Vk
        elif self.RS[inst].op == "OR":
            return self.RS[inst].Vj | self.RS[inst].Vk
        elif self.RS[inst].op == "NOT":
            return ~self.RS[inst].Vj
        elif self.RS[inst].op == "LW":
            return self.RS[inst].Vj + self.RS[inst].A
        elif self.RS[inst].op == "SW":
            return self.RS[inst].Vj + self.RS[inst].A
        elif self.RS[inst].op == "BLT":
            return self.RS[inst].A if self.RS[inst].Vj < self.RS[inst].Vk else self.pc
        elif self.RS[inst].op == "BGT":
            return self.RS[inst].A if self.RS[inst].Vj > self.RS[inst].Vk else self.pc
        elif self.RS[inst].op == "BEQ":
            return self.RS[inst].A if self.RS[inst].Vj == self.RS[inst].Vk else self.pc
        elif self.RS[inst].op == "BNE":
            return self.RS[inst].A if self.RS[inst].Vj != self.RS[inst].Vk else self.pc
        elif self.RS[inst].op == "J":
            return self.RS[inst].A
        else:
            pass

    def write(self):
        for unit in self.addUnit:
            if unit.busy and self.RS[unit.inst].exec == 0:
                v : int = self.execute(unit.inst)
                if self.RS[unit.inst].op in DESVIO:
                    self.pc = v
                else:
                    for register in self.registerStat:
                        if register.Qi == unit.inst:
                            register.Qi = None
                            register.value = v
                    for rs in self.RS:
                        if rs.Qj == unit.inst:
                            rs.Vj = v
                            rs.Qj = None
                        if rs.Qk == unit.inst:
                            rs.Vk = v
                            rs.Qk = None
                self.instrucoes -= 1
                self.RS[unit.inst] = ReservationStation()
                unit.busy = False
        for unit in self.mulUnit:
            if unit.busy and self.RS[unit.inst].exec == 0:
                v : int = self.execute(unit.inst)

                for register in self.registerStat:
                    if register.Qi == unit.inst:
                        register.Qi = None
                        register.value = v
                for rs in self.RS:
                    if rs.Qj == unit.inst:
                        rs.Vj = v
                        rs.Qj = None
                    if rs.Qk == unit.inst:
                        rs.Vk = v
                        rs.Qk = None
                self.instrucoes -= 1
                self.RS[unit.inst] = ReservationStation()
                unit.busy = False
        for unit in self.ldUnit:
            if unit.busy and self.RS[unit.inst].exec == 0:
                v : int = self.execute(unit.inst)
                print(v)
                if self.RS[unit.inst].op == "SW":
                    for memory in self.memory:
                        if memory.Qi == unit.inst:
                            memory.Qi = None
                            memory.value = v
                else:
                    for register in self.registerStat:
                        if register.Qi == unit.inst:
                            register.Qi = None
                            register.value = v
                for rs in self.RS:
                    if rs.Qj == unit.inst:
                        rs.Vj = v
                        rs.Qj = None
                    if rs.Qk == unit.inst:
                        rs.Vk = v
                        rs.Qk = None
                self.instrucoes -= 1
                self.RS[unit.inst] = ReservationStation()
                unit.busy = False

    def printStatus(self):
        print("Clock: ", self.clock)
        print("    RS    | BUSY  | Clock |   OP   |   Vj  |   Vk  |   Qj  |   Qk  |   A   |")
        for i in range(16):
            if self.RS[i].busy:
                print("ADD  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(16, 32):
            if self.RS[i].busy:
                print("MUL  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(32, 48):
            if self.RS[i].busy:
                print("LOAD | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        print("\nRegistradores:")
        print("Reg | Qi | Value")
        for i in range(11):
            print("{:2d} | {!r:5} | {:3d} ".format(i, self.registerStat[i].Qi, self.registerStat[i].value))
        print("\nMemoria:")
        print("Mem | Qi | Value")
        for i in range(5):
            print("{:2d} | {!r:5} | {:3d} ".format(i, self.memory[i].Qi, self.memory[i].value))
        
        outputFile.write("Clock: {}\n".format(self.clock))
        outputFile.write("    RS    | BUSY  | Clock |   OP   |   Vj  |   Vk  |   Qj  |   Qk  |   A   |\n")
        for i in range(16):
            if self.RS[i].busy:
                outputFile.write("ADD  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(16, 32):
            if self.RS[i].busy:
                outputFile.write("MUL  | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        for i in range(32, 48):
            if self.RS[i].busy:
                outputFile.write("LOAD | {:2d} | {!r:5} | {!r:5} | {!r:6s} | {!r:5} | {!r:5} | {!r:5} | {!r:5} | {!r:5} |\n".format(i, self.RS[i].busy, self.RS[i].exec, self.RS[i].op, self.RS[i].Vj, self.RS[i].Vk, self.RS[i].Qj, self.RS[i].Qk, self.RS[i].A))
        outputFile.write("\nRegistradores:\n")
        outputFile.write("Reg | Qi | Value\n")
        for i in range(11):
            outputFile.write("{:2d} | {!r:5} | {:3d} \n".format(i, self.registerStat[i].Qi, self.registerStat[i].value))
        outputFile.write("\nMemoria:\n")
        outputFile.write("Mem | Qi | Value\n")
        for i in range(5):
            outputFile.write("{:2d} | {!r:5} | {:3d} \n".format(i, self.memory[i].Qi, self.memory[i].value))
        outputFile.write("\n")
        """
        print("\nUnidades:")
        print("ADD\nUnit | BUSY  | Inst")
        for i in range(3):
            print("{:4d} | {!r:5} | {!r:5} ".format(i, self.addUnit[i].busy, self.addUnit[i].inst))
        print("MUL\nUnit | BUSY  | Inst")
        for i in range(3):
            print("{:4d} | {!r:5} | {!r:5} ".format(i, self.mulUnit[i].busy, self.mulUnit[i].inst))
        print("LD\nUnit | BUSY  | Inst")
        for i in range(3):
            print("{:4d} | {!r:5} | {!r:5} ".format(i, self.ldUnit[i].busy, self.ldUnit[i].inst))
        """

    # Executa o algoritmo de Tomasulo
    def run(self):
        #for inst in self.instList:
        #    print(inst)
        self.search()
        self.printStatus()
        self.clock += 1
        # input()
        self.issue()
        while self.instrucoes > 0:
            self.write()
            self.setUnits()
            self.printStatus()
            self.search()
            self.clock += 1
            # input()
            self.issue()

def lexer(inputFile : TextIO) -> List[List[str]]:
    instList : List[str] = []
    
    for line in inputFile:
        instList.append(line.replace(',', '').split()) # TODO: retirar o replace caso entrada não possua ','

    return instList

def main():
    try:
        inputFile = open("input.txt")
    except:
        print("Arquivo de leitura não encontrado")
        sys.exit()
    
    instList : List[List[str]] = lexer(inputFile)
    
    tomasulo = Tomasulo(instList)

    tomasulo.run()

if __name__ == "__main__":
    main()