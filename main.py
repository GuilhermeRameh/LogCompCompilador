import sys
from abc import ABC

############### Lista de palavras reservadas #############

reservedWords = [
    "println",
    "while",
    "if", 
    "else",
    "end",
]

################ Global SymbolTable ###################

class SymbolTable:
    def __init__(self) -> None:
        self.dicionario = {}
    
    def Getter(self, key):
        return self.dicionario[key]

    def Setter(self, key, value):
        self.dicionario[key] = value

global ST
ST = SymbolTable()

############### Node and Ops Classes ##############

class Node(ABC):
    def Evaluate(self):
        pass

class While(Node):
    def __init__(self, children) -> None:
        self.children = children

    def Evaluate(self):
        condition = self.children[0].Evaluate()
        while condition:
            self.children[1].Evaluate()

class If(Node):
    def __init__(self, children) -> None:
        self.children = children

    def Evaluate(self):
        if self.children[0].Evaluate():
            self.children[1].Evaluate()
        else:
            if len(self.children) == 3:
                self.children[2].Evaluate()


class Identifier(Node):
    def __init__(self, value) -> None:
        self.value = value
        self.children = [Node(x) for x in []]
    
    def Evaluate(self):
        return ST.Getter(self.value)

class Print(Node):
    def __init__(self, children) -> None:
        self.children = children
    
    def Evaluate(self):
        print(self.children[0].Evaluate())
    
class Assignment(Node):
    def __init__(self, children) -> None:
        self.children = children
    
    def Evaluate(self):
        ST.Setter(self.children[0].value, self.children[1].Evaluate())
        
class Block(Node):
    def __init__(self, children) -> None:
        self.children = children

    def Evaluate(self):
        for child in self.children:
            child.Evaluate()

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
        elif self.value=="&&":
            return self.children[0].Evaluate() and self.children[1].Evaluate()
        elif self.value=="||":
            return self.children[0].Evaluate() or self.children[1].Evaluate()
        elif self.value=="==":
            return self.children[0].Evaluate() == self.children[1].Evaluate()
        elif self.value=="<":
            return self.children[0].Evaluate() < self.children[1].Evaluate()
        elif self.value==">":
            return self.children[0].Evaluate() > self.children[1].Evaluate()

class UnOp(Node):
    def __init__(self, value, children) -> None:
        self.value = value
        self.children = children

    def Evaluate(self):
        if self.value=="-":
            return -self.children[0].Evaluate()
        elif self.value=="!":
            return not(self.children[0].Evaluate())
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

            if letra=="\n":
                tipo = "NEXTLINE"
                self.position += 1

            # NOTE: números 
            if letra.isnumeric():
                while letra in ["0","1","2","3","4","5","6","7","8","9"]:
                    tipo = "INT"
                    valor += letra
                    self.position += 1
                    if self.position >= len(self.source):
                        break
                    letra = self.source[self.position]
                if letra.isalpha() or letra == "_":
                    raise Exception(f'ERRO SINTÁTICO:\n    > Há uma entrada no código que começa com um número e continua com outras letras do alfabeto.')

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

            # NOTE: Lidando com o =
            elif letra == "=":
                tipo = "ASSIGN"
                valor = letra
                self.position += 1
                letra = self.source[self.position]
                # NOTE: Lidando com o ==, igualdade booleana
                if letra == "=":
                    tipo = "EQUAL"
                    valor += letra
                    self.position += 1

            # NOTE: Lidando com <, >
            elif letra == "<":
                tipo = "LESSTHEN"
                valor = letra
                self.position += 1
            
            elif letra == ">":
                tipo = "GREATERTHEN"
                valor = letra
                self.position += 1

            # NOTE: Lidando com !, && e || (not, and e or)

            elif letra == "!":
                tipo = "NOT"
                valor = letra
                self.position += 1
            
            elif letra == "&":
                valor = letra
                self.position += 1
                letra = self.source[self.position]
                if letra == "&":
                    tipo = "AND"
                    valor += letra
                    self.postion += 1
                else:
                    raise Exception(f"ERRO TOKENIZER:\n > Usou apenas um &, devem ser dois: '&&'")
                  
            elif letra == "|":
                valor = letra
                self.position += 1
                letra = self.source[self.position]
                if letra == "|":
                    tipo = "OR"
                    valor += letra
                    self.postion += 1
                else:
                    raise Exception(f"ERRO TOKENIZER:\n > Usou apenas um &, devem ser dois: '||'")
                


            # NOTE: Lida com palavras / variaveis
            if letra.isalpha():
                tipo = "IDENTIFIER"
                while letra.isalnum() or letra=="_":
                    valor += letra
                    self.position += 1
                    if (self.position<len(self.source)):
                        letra=self.source[self.position]
                    else:
                        break

                if valor in reservedWords:
                    tipo = valor.upper()            
    

        if tipo != None and valor != None:
            tokenCreate = Token(tipo, valor)
            self.next = tokenCreate

############## Parser Class ########################

class Parser:
    def __init__(self):
        self.tokenizer = Tokenizer

    def parseRelExpression(self):
        thisNode = self.parseExpression()

        if self.tokenizer.next.tipo == "EQUAL":
            self.tokenizer.selectNext()
            thisNode = BinOp("==", [thisNode, self.parseExpression()])
        elif self.tokenizer.next.tipo == "LESSTHEN":
            self.tokenizer.selectNext()
            thisNode = BinOp("<", [thisNode, self.parseExpression()])
        elif self.tokenizer.next.tipo == "GREATERTHEN":
            self.tokenizer.selectNext()
            thisNode = BinOp(">", [thisNode, self.parseExpression()])

        return thisNode

    def parseStatment(self):
        if self.tokenizer.next.tipo == "IDENTIFIER":
            idNode = Identifier(self.tokenizer.next.valor)
            self.tokenizer.selectNext()
            if self.tokenizer.next.tipo == "ASSIGN":
                self.tokenizer.selectNext()
                expressionNode = self.parseExpression()
                if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                    raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
                self.tokenizer.selectNext()
                return Assignment([idNode, expressionNode])
            else:
                raise Exception(f"ERRO PARSER:\n > Variavel sem assign ou fora de println")

        elif self.tokenizer.next.tipo == "PRINTLN":
            self.tokenizer.selectNext()
            printNode = Print([self.parseExpression()])
            return printNode
        
        # NEW
        elif self.tokenizer.next.tipo == "WHILE":
            self.tokenizer.selectNext()
            condition = self.parseRelExpression()
            self.tokenizer.selectNext()
            if self.tokenizer.next.tipo == "NEXTLINE":
                childrenList = []
                while self.tokenizer.next.tipo != "END":
                    childrenList.append(self.parseStatment())
                    self.tokenizer.selectNext()
                self.tokenizer.selectNext()
                blockNode = Block(childrenList)
                whileNode = While([condition, blockNode])
                if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                    raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
                self.tokenizer.selectNext()
            else:
                raise Exception(f"ERRO PARSER:\n    > Chamada da função 'while' incorreta.")
            return whileNode
        
        # NEW
        elif self.tokenizer.next.tipo == "IF":
            self.tokenizer.selectNext()
            condition = self.parseRelExpression()
            if self.tokenizer.next.tipo == "NEXTLINE":
                self.tokenizer.selectNext()
                childrenList = []
                while self.tokenizer.next.tipo != "END":
                    if self.tokenizer.next.tipo == "ELSE":
                        break
                    childrenList.append(self.parseStatment())
                    self.tokenizer.selectNext()
                self.tokenizer.selectNext()
                nodeTrue = Block(childrenList)
                if self.tokenizer.next.tipo == "ELSE":
                    childrenList = []
                    while self.tokenizer.next.tipo != "END":
                        childrenList.append(self.parseStatment())
                        self.tokenizer.selectNext()
                    self.tokenizer.selectNext()
                    nodeFalse = Block(childrenList)
                    ifNode = If([condition, nodeTrue, nodeFalse])
                else:
                    ifNode = If([condition, nodeTrue])
                if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                    raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\n'")
                self.tokenizer.selectNext()
                return ifNode
        
        elif self.tokenizer.next.tipo == "NEXTLINE":
            self.tokenizer.selectNext()
            return NoOp()
    
        else:
            raise Exception(f"ERRO PARSER:\n > Frase começando com um número")  


    def parseBlock(self):
        childrenList = []
        while self.tokenizer.next.tipo != "EOF":
            childrenList.append(self.parseStatment())
        return Block(childrenList)


    def parseFactor(self):
        thisNode = NoOp()

        if self.tokenizer.next.tipo == "INT":
            #copia para resultado e pega proximo valor
            # bufferFactor = int(self.tokenizer.next.valor)
            thisNode = IntVal(int(self.tokenizer.next.valor))
            self.tokenizer.selectNext()
            return thisNode

        elif self.tokenizer.next.tipo == "IDENTIFIER":
            thisNode = Identifier(self.tokenizer.next.valor)
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
             # NEW
            elif self.tokenizer.next.tipo == "NOT":
                self.tokenizer.selectNext()
                thisNode = UnOp("!", [self.parseFactor()])


            elif self.tokenizer.next.tipo == "OPENPAR":
                self.tokenizer.selectNext()
                # bufferFactor = self.parseExpression()
                thisNode = self.parseRelExpression()
                if self.tokenizer.next.tipo != "CLOSEPAR":
                    raise Exception(f"ERRO PARSER:\n > Parênteses não fechados.")
                self.tokenizer.selectNext()

            # NEW
            elif self.tokenizer.next.tipo == "READLN":
                self.tokenizer.selectNext()
                if self.tokenizer.next.tipo == "OPENPAR":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.tipo != "CLOSEPAR":
                        raise Exception(f"ERRO PARSER:\n > Parênteses não fechados.")
                    self.tokenizer.selectNext()
                    return IntVal(int(input()))
                else:
                    raise Exception(f"ERRO PARSER:\n    > invocação de 'readln' incorreta.")

            else:
                raise Exception(f"ERRO PARSER:\n > Frase acabou em um token não numérico ou repitiu tokens não numéricos inválidos")  
            return thisNode

    def parseTerm(self):
        thisNode = self.parseFactor()
        

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

            # NEW
            if self.tokenizer.next.tipo == "AND":
                self.tokenizer.selectNext()
                thisNode = BinOp("&&", [thisNode, self.parseFactor()])

        return thisNode
       
    def parseExpression(self):

        thisNode = self.parseTerm()

        #enquanto token for +, -, *, /
        while self.tokenizer.next.tipo in ["PLUS", "MINUS", "MULT", "DIV", "OPENPAR", "OR", "AND"]:
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
            
            # NEW
            if self.tokenizer.next.tipo == "OR":
                self.tokenizer.selectNext()
                thisNode = BinOp("||", [thisNode, self.parseTerm()])


        return thisNode

    def run(self, code):
        self.tokenizer = Tokenizer(code)
        NodetoReturn = self.parseBlock()
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
debugCadeia = '''if 1==1
println(1)
end
'''

def main():
    if DEBUG==True:
        cadeia = debugCadeia
    else:
        cadeia = sys.argv[1]

    cadeia = Preprocess.filter(cadeia)

    parser = Parser()
    parser.run(cadeia)


if __name__ == "__main__":
    main()