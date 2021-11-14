from collections import deque
from typing import Deque, List, TextIO
import sys

ARITMETICA : List[str] = ["ADD", "ADDI", "SUB", "SUBI", "MUL", "DIV"]
LOGICA : List[str] = ["AND", "OR", "NOT"]
DESVIO : List[str] = ["BLT", "BGT", "BEQ","BNE", "J"]
MEMORIA : List[str] = ["LW", "SW"]

class ReservationStation:
    def __init__(self) -> None:
        self.busy = False
        self.op = None
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.A = None

class Register:
    def __init__(self) -> None:
        self.Qi = 0
        self.value = 0

class DataMemory:
    def __init__(self) -> None: 
        self.value = 0 # TODO: rever atributos depois

class FunctionalUnit: # TODO: nao sei se é necessario
    def __init__(self) -> None:
        pass

class Tomasulo:
    def __init__(self, instQueue : Deque[List[str]]) -> None:        
        self.clock : int = 0
        self.instQueue : Deque[List[str]] = instQueue
        self.memory : DataMemory = [DataMemory() for i in range(512)]
        self.registerStat : Register = [Register() for i in range(32)]
        self.RS : ReservationStation = [ReservationStation() for i in range(48)]
        # 48 estações de reserva sendo:
        # 0 - 15 : add e sub
        # 16 - 31 : mult e div
        # 32 - 47 : ld e st
        # como vão ser feitas as operações de desvio e logicas?

    # Realiza a busca da instrução na queue
    def search(self) -> List[str]:
        return self.instQueue.popleft()

    # Faz o despacho da instrução
    def issue(self, inst : List[str]):
        print(inst)
        op = inst[0]
        rd = inst[1]
        rs = inst[2]
        rt = inst[3]
        r = 0 # TODO: alguma coisa
        if op in ARITMETICA:
            # TODO : rs e rt tem que ser o numero do registrador ou faz rashmap
            if self.registerStat[rs].Qi != 0:
                self.RS[r].Qj = self.registerStat[rs].Qi
            else:
                self.RS[r].Vj = self.registerStat[rs].value
                self.RS[r].Qj = 0
            
            if self.registerStat[rt].Qi != 0:
                self.RS[r].Qk = self.registerStat[rt].Qi
            else:
                self.RS[r].Vk = self.registerStat[rt].value
                self.RS[r].Qk = 0
            
            self.RS[r].busy = True
            self.registerStat[rd].Qi = r
        elif op in LOGICA:
            pass
        elif op in DESVIO:
            pass
        elif op in MEMORIA:
            pass
        else:
            print(op)
            raise Exception("Instrução não reconhecida")

    # Executa as instruções
    def execute(self): #TODO: bem generico isso
        pass

    # Executa o algoritmo de Tomasulo
    #  TODO: A principio essa seria a função principal
    def run(self):
        #for inst in self.instQueue:
        #    print(inst)
        while len(self.instQueue) > 0:
            inst = self.search()
            self.issue(inst)
            self.clock += 1

def lexer(inputFile : TextIO) -> Deque[List[str]]:
    instQueue : Deque[str] = deque()
    
    for line in inputFile:
        instQueue.append(line.replace(',', '').split()) # TODO: retirar o replace caso entrada não possua ','

    return instQueue

def main():
    try:
        inputFile = open("input.txt")
    except:
        print("Arquivo de leitura não encontrado")
        sys.exit()
    
    instQueue : Deque[List[str]] = lexer(inputFile)

    tomasulo = Tomasulo(instQueue)

    tomasulo.run()

if __name__ == "__main__":
    main()