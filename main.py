import sys

################# TOKEN CLASS #####################
class Token:
    def __init__(self, tipo, valor) -> None:
        self.tipo = tipo
        self.valor = valor

############ PREPROCESS CLASS ######################

class Preprocess:
    def filter(doc):
        if ".txt" in doc:
            with open(doc, 'r') as file:
                print()
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
        bufferFactor = 0

        if self.tokenizer.next.tipo == "INT":
            #copia para resultado e pega proximo valor
            bufferFactor = int(self.tokenizer.next.valor)
            self.tokenizer.selectNext()
            return bufferFactor
        
        else:
            if self.tokenizer.next.tipo == "PLUS":
                self.tokenizer.selectNext()
                bufferFactor += self.parseFactor()
            elif self.tokenizer.next.tipo == "MINUS":
                self.tokenizer.selectNext()
                bufferFactor -= self.parseFactor()
            elif self.tokenizer.next.tipo == "OPENPAR":
                self.tokenizer.selectNext()
                bufferFactor = self.parseExpression()
                if self.tokenizer.next.tipo != "CLOSEPAR":
                    raise Exception(f"ERRO PARSER:\n > Parênteses não fechados.")
                self.tokenizer.selectNext()
                
            return bufferFactor

    def parseTerm(self):
        bufferTerm = self.parseFactor()

        #enquanto token for * ou /
        while self.tokenizer.next.tipo in ["MULT", "DIV"]:
            #Se for *
            if self.tokenizer.next.tipo == "MULT":
                self.tokenizer.selectNext()
                bufferTerm *= self.parseFactor()
               
            if self.tokenizer.next.tipo == "DIV":
                self.tokenizer.selectNext()
                bufferTerm //= self.parseFactor()

        return bufferTerm
       
    def parseExpression(self):

        resultado = self.parseTerm()

        #enquanto token for +, -, *, /
        while self.tokenizer.next.tipo in ["PLUS", "MINUS", "MULT", "DIV", "OPENPAR"]:
            #Se for +
            if self.tokenizer.next.tipo == "PLUS":
                self.tokenizer.selectNext()
                resultado += self.parseTerm() # Chamou TERM
            #Se for -
            if self.tokenizer.next.tipo == "MINUS":
                self.tokenizer.selectNext()
                resultado -= self.parseTerm() # Chamou TERM

        return resultado

    def run(self, code):
        self.tokenizer = Tokenizer(code)
        toReturn = self.parseExpression()
        #checa se terminou de consumir
        if self.tokenizer.next.tipo == "EOF":
            return toReturn
        else:
            raise Exception(f"ERRO PARSER:\n O parser saiu e não consumiu todos os tokens.")



#--------------------------------------------------------#
#                         MAIN                           #
#--------------------------------------------------------#

# NOTE: mudar DEBUG para True caso quiser definir manualmente a entrada
DEBUG = False
debugCadeia = "4/(1+1)*2 #Bruh"

def main():
    if DEBUG==True:
        cadeia = debugCadeia
    else:
        cadeia = sys.argv[1]

    cadeia = Preprocess.filter(cadeia)

    parser = Parser()
    print(parser.run(cadeia))


if __name__ == "__main__":
    main()