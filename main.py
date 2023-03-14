import sys
from abc import ABC, abstractmethod

############### Node and Ops Classes ##############

class Node(ABC):
   
    def Evaluate(self):
        pass


class BinOp(Node):
    def __init__(self, value, children) -> None:
            self.value = value
            self.children = children

    def Evaluate(self):
        if self.value=="+":
            return self.children[0].Evaluate()+self.children[1].Evaluate()
        elif self.value=="-":
            return self.children[0].Evaluate()-self.children[1].Evaluate()
        elif self.value=="*":
            return self.children[0].Evaluate()*self.children[1].Evaluate()
        elif self.value=="/":
            return self.children[0].Evaluate()//self.children[1].Evaluate()

class UnOp(Node):
    def __init__(self, value, children) -> None:
        self.value = value
        self.children = children

    def Evaluate(self):
        if self.value=="-":
            return -self.children[0].Evaluate()
        return self.children[0].Evaluate()

class IntVal(Node):
    def __init__(self, value) -> None:
        self.value = value
        self.children = [Node(x) for x in []]

    def Evaluate(self):
        return int(self.value)

class NoOp(Node):
    pass


################# TOKEN CLASS #####################
class Token:
    def __init__(self, tipo, valor) -> None:
        self.tipo = tipo
        self.valor = valor

############ PREPROCESS CLASS ######################

class Preprocess:
    def filter(doc):
        if ".jl" in doc:
            with open(doc, 'r') as file:
                Lines = file.readlines()
            toReturn = ""
            for line in Lines:
                lista = line.split("#")
                toReturn+=lista[0]
            return toReturn

        else:
            lista = doc.split("#")
            return lista[0]

############ TOKENIZER CLASS ######################
class Tokenizer:
    def __init__(self, source) -> None:
        self.source = source
        self.position = -1
        self.next = None
        self.selectNext()

    def selectNext(self):
        tipo = None
        valor = None
        if self.position == -1:
            self.position += 1  
        if self.position >= len(self.source):
            tipo = "EOF"
            valor = ""
        else:
            letra = self.source[self.position]
            valor = ""
            while letra == " ":
                self.position += 1
                if self.position < len(self.source):
                    letra = self.source[self.position]
                else:
                    letra = "END"
                    valor = ""
                    tipo = "EOF"

            # NOTE: números 
            if letra.isnumeric():
                while letra in ["0","1","2","3","4","5","6","7","8","9"]:
                    tipo = "INT"
                    valor += letra
                    self.position += 1
                    if self.position >= len(self.source):
                        break
                    letra = self.source[self.position]

            # NOTE: +, -, *, /
            elif letra == "+":
                tipo = "PLUS"
                valor = letra
                self.position += 1
            elif letra == "-":
                tipo = "MINUS"
                valor = letra
                self.position += 1
            elif letra == "*":
                tipo = "MULT"
                valor = letra
                self.position += 1
            elif letra == "/":
                tipo = "DIV"
                valor = letra
                self.position += 1

            # NOTE: Lidando com parenteses
            elif letra == "(":
                tipo = "OPENPAR"
                valor = letra
                self.position += 1
            elif letra == ")":
                tipo = "CLOSEPAR"
                valor = letra
                self.position += 1

        if tipo != None and valor != None:
            tokenCreate = Token(tipo, valor)
            self.next = tokenCreate

############## Parser Class ########################

class Parser:
    def __init__(self):
        self.tokenizer = Tokenizer

    def parseFactor(self):
        # TODO: mesma parada
        bufferFactor = 0
        thisNode = NoOp()

        if self.tokenizer.next.tipo == "INT":
            #copia para resultado e pega proximo valor
            # bufferFactor = int(self.tokenizer.next.valor)
            thisNode = IntVal(int(self.tokenizer.next.valor))
            self.tokenizer.selectNext()
            return thisNode
        
        else:
            if self.tokenizer.next.tipo == "PLUS":
                self.tokenizer.selectNext()
                # bufferFactor += self.parseFactor()
                thisNode = UnOp("+", [self.parseFactor()])
            elif self.tokenizer.next.tipo == "MINUS":
                self.tokenizer.selectNext()
                # bufferFactor -= self.parseFactor()
                thisNode = UnOp("-", [self.parseFactor()])
            elif self.tokenizer.next.tipo == "OPENPAR":
                self.tokenizer.selectNext()
                # bufferFactor = self.parseExpression()
                thisNode = self.parseExpression()
                if self.tokenizer.next.tipo != "CLOSEPAR":
                    raise Exception(f"ERRO PARSER:\n > Parênteses não fechados.")
                self.tokenizer.selectNext()

            else:
                raise Exception(f"ERRO PARSER:\n > Frase acabou em um token não numérico ou repitiu tokens não numéricos inválidos")  
            return thisNode

    def parseTerm(self):
        # TODO: ja sabe né
        bufferTerm = self.parseFactor()
        thisNode = bufferTerm
        

        #enquanto token for * ou /
        while self.tokenizer.next.tipo in ["MULT", "DIV"]:
            #Se for *
            if self.tokenizer.next.tipo == "MULT":
                self.tokenizer.selectNext()
                thisNode = BinOp("*", [thisNode, self.parseFactor()])
                # bufferTerm *= self.parseFactor()
               
            if self.tokenizer.next.tipo == "DIV":
                self.tokenizer.selectNext()
                thisNode = BinOp("/", [thisNode, self.parseFactor()])
                # bufferTerm //= self.parseFactor()

        return thisNode
       
    def parseExpression(self):

        # TODO: Depois que der certo, isso é redundante, arrumar
        resultado = self.parseTerm()
        thisNode = resultado

        #enquanto token for +, -, *, /
        while self.tokenizer.next.tipo in ["PLUS", "MINUS", "MULT", "DIV", "OPENPAR"]:
            #Se for +
            if self.tokenizer.next.tipo == "PLUS":
                self.tokenizer.selectNext()
                thisNode = BinOp("+", [thisNode, self.parseTerm()])
                # resultado += self.parseTerm() # Chamou TERM
            #Se for -
            if self.tokenizer.next.tipo == "MINUS":
                self.tokenizer.selectNext()
                thisNode = BinOp("-", [thisNode, self.parseTerm()])
                # resultado -= self.parseTerm() # Chamou TERM

        return thisNode

    def run(self, code):
        self.tokenizer = Tokenizer(code)
        NodetoReturn = self.parseExpression()
        #checa se terminou de consumir
        if self.tokenizer.next.tipo == "EOF":
            return NodetoReturn.Evaluate()
        else:
            raise Exception(f"ERRO PARSER:\n O parser saiu e não consumiu todos os tokens.")



#--------------------------------------------------------#
#                         MAIN                           #
#--------------------------------------------------------#

# NOTE: mudar DEBUG para True caso quiser definir manualmente a entrada
DEBUG = False
debugCadeia = "-1"

def main():
    if DEBUG==True:
        cadeia = debugCadeia
    else:
        cadeia = sys.argv[1]

    cadeia = Preprocess.filter(cadeia)

    parser = Parser()
    finalNode = parser.run(cadeia)
    print(finalNode)


if __name__ == "__main__":
    main()