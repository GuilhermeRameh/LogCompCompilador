import sys
# from abc import ABC
import uuid

############### CLASSE WRITER ############################

class Writer:
    def __init__(self) -> None:
        doc = open("modelo.asm", "r")
        self.input = doc.read()
        doc.close()
        self.header = self.input.split("; codigo gerado pelo compilador")[0]
        self.footer = self.input.split("; codigo gerado pelo compilador")[1]

    def Prep(self, filename):
        self.output = open(f"{filename}.asm", "w")

    def Write(self, string):
        self.output.write(string)

    def Head(self):
        self.Write(self.header)

    def Foot(self):
        self.Write(self.footer)

    def Close(self):
        self.output.close()

global writer
writer = Writer()

############### Lista de palavras reservadas #############

reservedWords = [
    "println",
    "while",
    "if", 
    "else",
    "end",
    "readline",
]

tipagem = [
    "Int",
    "String",
]

################ Global SymbolTable ###################

class SymbolTable:
    def __init__(self) -> None:
        self.dicionario = {}
    
    def Getter(self, key):
        if key not in self.dicionario.keys():
            raise Exception(f"ERRO SymbolTable:\n   > a variável '{key}' não foi declarada anteriormente.")
        return self.dicionario[key]

    def Setter(self, key, value):
        # NOTE: Verificação de tipagem
        if type(value)==tuple:
            if (value[0] == self.dicionario[key][0]):
                self.dicionario[key] = value + (self.dicionario[key][2],)
            else:
                raise Exception(f"ERRO SymbolTable:\n   > Não é possível atribuir o valor de tipo: {value[0]} para uma variável {self.dicionario[key][0]}.")
        else:
            self.dicionario[key] = (self.dicionario[key][0], value, self.dicionario[key][2])
        
    def Create(self, key, value):
        if key in self.dicionario.keys():
            raise Exception(f"ERRO SymbolTable:\n   > Essa variável já foi declarada")
        self.dicionario[key] = value + ((-(len(self.dicionario) + 1) * 4),)


global ST
ST = SymbolTable()

############### Node and Ops Classes ##############

class Node():
    unique_id = 0
    def __init__(self) -> None:
        Node.unique_id += 1
        self.id = Node.unique_id


    def Evaluate(self):
        pass

class VarDec(Node):
    def __init__(self, value, children) -> None:
        super().__init__()
        self.value = value
        self.children = children
        self.id = uuid.uuid4()

    def Evaluate(self):
        tipo = self.value
        if len(self.children) == 1:
            if tipo=="Int": atribuicao=("INT",0)
            elif tipo=="String": atribuicao=("STRING","")
            ST.Create(self.children[0].value, atribuicao)

            # NOTE: Parte em assembly
            writer.Write(f"\nPUSH DWORD 0")
        elif len(self.children) == 2:
            ST.Create(self.children[0].value, self.children[1].Evaluate())

            #NOTE: Parte em assembly
            writer.Write(f"\nPUSH DWORD 0")

class While(Node):
    def __init__(self, children) -> None:
        super().__init__()
        self.children = children

    def Evaluate(self):
        writer.Write(f"\nLOOP_{self.id}:") #DONE: Implementar labels dinamicas
        
        condition = self.children[0].Evaluate()
        if condition:
            condition="True"
        else: condition="False"
        # while condition:
        #     self.children[1].Evaluate()
        #     condition = self.children[0].Evaluate()
       
        writer.Write(f"\nMOV EBX, {condition}")
        writer.Write("\nCMP EBX, False")
        writer.Write(f"\nJE EXIT_{self.id}") # DONE: Label dinamica

        self.children[1].Evaluate()

        writer.Write(f"\nJMP LOOP_{self.id}") # DONE: dinamica
        writer.Write(f"\nEXIT_{self.id}:") # DONE: dinamica

class If(Node):
    def __init__(self, children) -> None:
        super().__init__()
        self.children = children

    def Evaluate(self):
        condition = self.children[0].Evaluate()
        if condition:
            condition="True"
        else: condition="False"
        writer.Write(f"\nMOV {condition}, EBX")
        writer.Write(f"CMP EBX, False")
        writer.Write(f"JE IF_{self.id}")

        if len(self.children)==3:
            self.children[2].Evaluate()
        
        writer.Write(f"JMP END_IF_{self.id}")
        writer.Write(f"IF_{self.id}")

        self.children[1].Evaluate()

        writer.Write(f"END_IF_{self.id}")


class Identifier(Node):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.children = [Node(x) for x in []]
    
    def Evaluate(self):
        to_ret = ST.Getter(self.value)
        #NOTE: parte em assembly
        writer.Write(f"\nMOV EBX, [EBP{to_ret[2]}]")
        return to_ret


class Print(Node):
    def __init__(self, children) -> None:
        super().__init__()
        self.children = children
    
    def Evaluate(self):
        toPrint = self.children[0].Evaluate()
        # if type(toPrint) == tuple:
        # NOTE: Parte em assembly
        writer.Write(f"\nPUSH EBX")
        writer.Write(f"\nCALL print")
        writer.Write(f"\nPOP EBX")

            # print(self.children[0].Evaluate()[1])
        # else: 
            # print(self.children[0].Evaluate())
    
class Assignment(Node):
    def __init__(self, children) -> None:
        super().__init__()
        self.children = children
    
    def Evaluate(self):
        ST.Setter(self.children[0].value, self.children[1].Evaluate())
        shift = self.children[0].Evaluate()[2]

        #NOTE: Assembly
        writer.Write(f"\nMOV [EBP{shift}], EBX")
        
class Block(Node):
    def __init__(self, children) -> None:
        super().__init__()
        self.children = children

    def Evaluate(self):
        for child in self.children:
            child.Evaluate()

class BinOp(Node):
    def __init__(self, value, children) -> None:
        super().__init__()
        self.value = value
        self.children = children

    def Evaluate(self):
        child0Type = None
        child1Type = None
        child0 = self.children[0].Evaluate()
        writer.Write(f"\nPUSH EBX")
        child1 = self.children[1].Evaluate()
        writer.Write(f"\nPOP EAX")


        if self.value=="+":
            writer.Write(f"\nADD EAX, EBX")
            # return child0+child1
        elif self.value=="-":
            writer.Write(f"\nSUB EAX, EBX")
            # return child0-child1
        elif self.value=="*":
            writer.Write(f"\nIMUL EAX, EBX")
            # return child0*child1
        elif self.value=="/":
            writer.Write(f"\nIDIV EAX, EBX")
            # return child0//child1
        elif self.value=="&&":
            writer.Write(f"\nAND EAX, EBX")
            # return 1 if child0 and child1 else 0
        elif self.value=="||":
            writer.Write(f"\nOR EAX, EBX")
            # return 1 if child0 or child1 else 0
        elif self.value=="==":
            writer.Write(f"\nCMP EAX, EBX")
            writer.Write(f"\nCALL binop_je")
            # return 1 if child0 == child1 else 0
        elif self.value=="<":
            writer.Write(f"\nCMP EAX, EBX")
            writer.Write(f"\nCALL binop_jl")
            # return 1 if child0 < child1 else 0
        elif self.value==">":
            writer.Write(f"\nCMP EAX, EBX")
            writer.Write(f"\nCALL binop_jg")
            # return 1 if child0 > child1 else 0
        # # NEW
        # elif self.value==".":
        #     return str(child0) + str(child1)
        writer.Write(f"\nMOV EBX, EAX")

class UnOp(Node):
    def __init__(self, value, children) -> None:
        super().__init__()
        self.value = value
        self.children = children

    def Evaluate(self):
        # if type(self.children[0].Evaluate())==tuple:
        #     child0 = self.children[0].Evaluate()[1]
        # else: child0 = self.children[0].Evaluate()
        child0 = self.children[0].Evaluate()

        if self.value=="-":
            writer.Write(f"\nMUL EBX, -1")
            # return -child0
        elif self.value=="!":
            writer.Write(f"\nNOT EBX")
            # return not(child0)
        # return child0

class IntVal(Node):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.children = [Node(x) for x in []]

    def Evaluate(self):
        writer.Write(f"\nMOV EBX, {self.value[1]}")
        return self.value
    
class StringVal(Node):
    def __init__(self, value) -> None:
        self.value = value
        self.children = [Node(x) for x in []]

    def Evaluate(self):
        return self.value

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
            return toReturn, doc.split(".")[1][1:]

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

            #NEW
            #NOTE: Lidando com operador CONCATENAR STRING
            elif letra == ".":
                tipo = "CONCAT"
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
                    self.position += 1
                else:
                    raise Exception(f"ERRO TOKENIZER:\n > Usou apenas um &, devem ser dois: '&&'")
                  
            elif letra == "|":
                valor = letra
                self.position += 1
                letra = self.source[self.position]
                if letra == "|":
                    tipo = "OR"
                    valor += letra
                    self.position += 1
                else:
                    raise Exception(f"ERRO TOKENIZER:\n > Usou apenas um |, devem ser dois: '||'")
                
            # NOTE: Lidando com as declaracoes de variaveis '::'
            elif letra == ":":
                valor = letra
                self.position += 1
                letra = self.source[self.position]
                if letra == ":":
                    tipo = "VARDEC"
                    valor += letra
                    self.position += 1
                else:
                    raise Exception(f"ERRO TOKENIZER:\n > Usou apenas um :, devem ser dois: '::'")
                
            # NOTE: Lida com Strings
            if letra == '"':
                tipo = "STRING"
                self.position += 1
                letra = self.source[self.position]
                while letra != '"':
                    valor += letra
                    self.position += 1
                    if (self.position<len(self.source)):
                        letra=self.source[self.position]
                    else: raise Exception(f"ERRO Tokenizer:\n   > Não fechou as aspas de uma string.")
                self.position += 1

            # NOTE: Lida com palavras / variaveis
            if letra.isalpha() and tipo != "EOF":
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
                if valor in tipagem:
                    tipo = "TYPE"        
    

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
                expressionNode = self.parseRelExpression()
                if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                    raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
                self.tokenizer.selectNext()
                return Assignment([idNode, expressionNode])
            # NEW: Lidando com declarações de variáveis
            elif self.tokenizer.next.tipo == "VARDEC":
                self.tokenizer.selectNext()
                if self.tokenizer.next.tipo == "TYPE":
                    tipo = self.tokenizer.next.valor
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.tipo == "ASSIGN":
                        self.tokenizer.selectNext()
                        expressionNode = self.parseRelExpression()
                        if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                            raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
                        self.tokenizer.selectNext()
                        return VarDec(tipo ,[idNode, expressionNode])
                    elif self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                        raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
                    return VarDec(tipo, [idNode])

                else:
                    raise Exception(f"ERRO PARSER:\n > Declaração de variável não usou tipagem corretamente.")
            else:
                raise Exception(f"ERRO PARSER:\n > Variavel sem assign ou fora de println")

        elif self.tokenizer.next.tipo == "PRINTLN":
            self.tokenizer.selectNext()
            printNode = Print([self.parseExpression()])
            if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
            return printNode

        elif self.tokenizer.next.tipo == "WHILE":
            # Consome token "while"
            self.tokenizer.selectNext()
            # Consome e salva condição a partir de RelExpression
            condition = self.parseRelExpression()
            
            if self.tokenizer.next.tipo == "NEXTLINE":
                # Consome \n
                self.tokenizer.selectNext()

                childrenList = []
                while self.tokenizer.next.tipo != "END":
                    childrenList.append(self.parseStatment())
                    
                # Consome o "end"
                self.tokenizer.selectNext()

                blockNode = Block(childrenList)
                whileNode = While([condition, blockNode])
                if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                    raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
                # Consome \n ou final
                self.tokenizer.selectNext()
            else:
                raise Exception(f"ERRO PARSER:\n    > Chamada da função 'while' incorreta.")
            return whileNode
        
        elif self.tokenizer.next.tipo == "IF":
            # Consome o token "if"
            self.tokenizer.selectNext()
            # Guarda a condição dado a repsosta de um RelExpression
            condition = self.parseRelExpression()
            # Verifica \n
            if self.tokenizer.next.tipo == "NEXTLINE":
                # Consome \n
                self.tokenizer.selectNext()

                childrenList = []
                while self.tokenizer.next.tipo != "END" and self.tokenizer.next.tipo != "EOF":
                    childrenList.append(self.parseStatment())
                    if self.tokenizer.next.tipo == "ELSE":
                        break
                # Salva o node caso a condição seja verdade
                nodeTrue = Block(childrenList)

                # Se tiver o else
                if self.tokenizer.next.tipo == "ELSE":
                    # Consome o token de else
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.tipo != "NEXTLINE":
                        raise Exception(f"ERRO PARSER:\n    > Chamou 'else' de maneira incorreta")
                    # Consome o \n
                    self.tokenizer.selectNext()

                    childrenList = []
                    while self.tokenizer.next.tipo != "END":
                        childrenList.append(self.parseStatment())
                    # Consome o end
                    self.tokenizer.selectNext()
                        
                    nodeFalse = Block(childrenList)
                    ifNode = If([condition, nodeTrue, nodeFalse])

                else:
                    # Consome o "end" se nao tiver else
                    self.tokenizer.selectNext()
                    ifNode = If([condition, nodeTrue])

                if self.tokenizer.next.tipo != "NEXTLINE" and self.tokenizer.next.tipo != "EOF":
                    raise Exception(f"ERRO PARSER:\n > Devia ter pulado de linha com '\\n'")
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
            thisNode = IntVal((self.tokenizer.next.tipo, int(self.tokenizer.next.valor)))
            self.tokenizer.selectNext()
            return thisNode

        elif self.tokenizer.next.tipo == "IDENTIFIER":
            thisNode = Identifier(self.tokenizer.next.valor)
            self.tokenizer.selectNext()
            return thisNode
        
        elif self.tokenizer.next.tipo == "STRING":
            thisNode = StringVal((self.tokenizer.next.tipo, self.tokenizer.next.valor))
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

            elif self.tokenizer.next.tipo == "READLINE":
                self.tokenizer.selectNext()
                if self.tokenizer.next.tipo == "OPENPAR":
                    self.tokenizer.selectNext()
                    if self.tokenizer.next.tipo != "CLOSEPAR":
                        raise Exception(f"ERRO PARSER:\n > Parênteses não fechados.")
                    self.tokenizer.selectNext()
                    return IntVal(int(input()))
                else:
                    raise Exception(f"ERRO PARSER:\n    > invocação de 'readline' incorreta.")

            else:
                raise Exception(f"ERRO PARSER:\n > Frase acabou em um token não numérico ou repitiu tokens não numéricos inválidos")  
            return thisNode

    def parseTerm(self):
        thisNode = self.parseFactor()

        #enquanto token for * ou /
        while self.tokenizer.next.tipo in ["MULT", "DIV", "AND"]:
            #Se for *
            if self.tokenizer.next.tipo == "MULT":
                self.tokenizer.selectNext()
                thisNode = BinOp("*", [thisNode, self.parseFactor()])
                # bufferTerm *= self.parseFactor()
               
            if self.tokenizer.next.tipo == "DIV":
                self.tokenizer.selectNext()
                thisNode = BinOp("/", [thisNode, self.parseFactor()])
                # bufferTerm //= self.parseFactor()

            if self.tokenizer.next.tipo == "AND":
                self.tokenizer.selectNext()
                thisNode = BinOp("&&", [thisNode, self.parseFactor()])

        return thisNode
       
    def parseExpression(self):

        thisNode = self.parseTerm()

        #enquanto token for +, -, *, /
        while self.tokenizer.next.tipo in ["PLUS", "MINUS", "OR", "CONCAT"]:
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
            
            if self.tokenizer.next.tipo == "OR":
                self.tokenizer.selectNext()
                thisNode = BinOp("||", [thisNode, self.parseTerm()])
            
            #NEW
            if self.tokenizer.next.tipo == "CONCAT":
                self.tokenizer.selectNext()
                thisNode = BinOp(".", [thisNode, self.parseTerm()])


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
DEBUG = 0
debugCadeia = '''# v2.2 testing
x_1::Int

x_1 = readline()
if ((x_1 > 1) && !(x_1 < 1)) 
x_1 = 3

else 

x_1 = (-20+30)*4*3/40 # teste de comentario

end
println(x_1)
x_1 = readline()
if (x_1 > 1) && !(x_1 < 1)
x_1 = 3
else
x_1 = (-20+30)*12/40


end    
println(x_1)
while ((x_1 > 1) || (x_1 == 1)) 
x_1 = x_1 - 1
println(x_1)
end'''

def main():
    if DEBUG==True:
        cadeia = debugCadeia
    else:
        cadeia = sys.argv[1]

    cadeia, filename = Preprocess.filter(cadeia)

    writer.Prep(filename)
    writer.Head()
    writer.Write("; codigo gerado pelo compilador\n")

    parser = Parser()
    parser.run(cadeia)

    writer.Foot()
    writer.Close()


if __name__ == "__main__":
    main()



'''
TODO: 
[ ] - separar codigo asm em cabecalho, escrever o codigo a partir da AST aqui,  dps escreve rodapé.

returns -> MOV EBX valor (sempre em EBX)

NOTE:
IntVal - eval - MOV EBX (VALOR)

NOTE:
BinOp - eval - 
    eval filho 0
    PUSH EBX ; guarda EBX na pilha
    eval filho 1
    POP EAX # recupera valor para EAX

    ADD EAX, EBX ; muda operação
    MOV EBX, EAX ; como se fosse return

NOTE:
VAR DEC - eval -  (EBP - BASE DA PILHA, ESP - TOPO DA PILHA (STACK POINTER))
; primeira atribuição:
PUSH DWORD 0 

ASSIGNMENT
MOV [EBP - *SHIFT*], EBX

NOTE: 
IDENTIFIER
MOV EBX, [EBP - *SHIFT*]

NOTE:
PRINT
PUSH EBX ; empilha argumentos para printar
CALL print ; printa
POP EBX ; retira os argumentos do print da pilha pra continuar o jogo

NOTE:
WHILE
LABEL PRA COMEÇO DO WHILE *ESPECIFICO*
IDENTIFICADOR DE CADA NÓ, NO NÓ PAI

LOOP_34:
; COMPARAÇÃO RETORNA EM EBX
CMP EBX, False ; verifica se o resultado da comparação é falsa
JE EXIT_34 ;

; intruções filho 1 do while

JMP LOOP_34
EXIT_34


NOTE:
IF - TRETA

ELSE PRIMEIRO DEPOIS IF

; comparação retorna em ebx
CMP EBX, False ; verifica se o resultado da comparação é falsa
JE IF_N

; INSTRUÇÕES DO FILHO ELSE
JMP END_IF_N

IF_N:
;INSTRUCOES DO FILHO IF

END_IF_N:


CRIA MÉTODO WRITE PROS EVALUATE
'''