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
                
            if letra.isnumeric():
                while letra in ["0","1","2","3","4","5","6","7","8","9"]:
                    tipo = "INT"
                    valor += letra
                    self.position += 1
                    if self.position >= len(self.source):
                        break
                    letra = self.source[self.position]

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

        if tipo != None and valor != None:
            tokenCreate = Token(tipo, valor)
            self.next = tokenCreate
            print(f"Token: {tipo}, {valor}")

############## Parser Class ########################

class Parser:
    def __init__(self):
        self.tokenizer = Tokenizer

    def parseTerm(self):
        buffer = 0
        #Se o token atual for numero
        if self.tokenizer.next.tipo == "INT":
            #copia para resultado e pega proximo valor
            buffer = int(self.tokenizer.next.valor)
            self.tokenizer.selectNext()
            #enquanto token for + ou -
            while self.tokenizer.next.tipo in ["MULT", "DIV"]:
                #Se for +
                if self.tokenizer.next.tipo == "MULT":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.tipo == "INT":
                        buffer *= int(self.tokenizer.next.valor)
                    else:
                        raise Exception(f"ERRO SINTÁTICO:\n    >Era esperado um TOKEN do tipo 'INT', mas recebeu '{self.tokenizer.next.tipo}'")
                #Se for -
                if self.tokenizer.next.tipo == "DIV":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.tipo == "INT":
                        buffer = buffer//int(self.tokenizer.next.valor)
                    else:
                        raise Exception(f"ERRO SINTÁTICO:\n    >Era esperado um TOKEN do tipo 'INT', mas recebeu '{self.tokenizer.next.tipo}'")
                self.tokenizer.selectNext()
            return buffer
        else:
            raise Exception("ERRO SINTÁTICO:\n    >O primeiro TOKEN da cadeia deve ser do tipo 'INT'.")

    def parseExpression(self):

        resultado = self.parseTerm()

        #enquanto token for + ou -
        while self.tokenizer.next.tipo in ["PLUS", "MINUS", "MULT", "DIV"]:
            #Se for +
            if self.tokenizer.next.tipo == "PLUS":
                self.tokenizer.selectNext()
                resultado += self.parseTerm()
            #Se for -
            if self.tokenizer.next.tipo == "MINUS":
                self.tokenizer.selectNext()
                resultado -= self.parseTerm()
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

DEBUG = False
debugCadeia = "1*1 #Bruh"

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