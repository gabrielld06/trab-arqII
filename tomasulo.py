from collections import deque
from typing import Deque, List, TextIO
import sys

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
        self.Value = 0

class DataMemory:
    def __init__(self) -> None: 
        self.Value = 0 # TODO: rever atributos depois

class FunctionalUnit: # TODO: nao sei se é necessario
    def __init__(self) -> None:
        pass

class Tomasulo:
    def __init__(self, instQueue : Deque[str]) -> None:        
        self.clock : int = 0
        self.instQueue : Deque = instQueue
        self.memory : DataMemory = [DataMemory() for i in range(512)]
        self.registerStat : Register = [Register() for i in range(32)]
        self.RS : ReservationStation = [ReservationStation() for i in range(48)]
        # 48 estações de reserva sendo:
        # 0 - 15 : add e sub
        # 16 - 31 : mult e div
        # 32 - 47 : ld e st
        # como vão ser feitas as operações de desvio e logicas?

    # Realiza a busca da instrução na queue
    def search(self):
        pass

    # Faz o despacho da instrução
    def issue(self):
        pass

    # Executa as instruções
    def execute(self): #TODO: bem generico isso
        pass

    # Executa o algoritmo de Tomasulo
    #  TODO: A principio essa seria a função principal
    def run(self):
        for inst in self.instQueue:
            print(inst)

def lexer(inputFile : TextIO) -> Deque[str]:
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
    
    instQueue : Deque[str] = lexer(inputFile)

    tomasulo = Tomasulo(instQueue)

    tomasulo.run()

if __name__ == "__main__":
    main()