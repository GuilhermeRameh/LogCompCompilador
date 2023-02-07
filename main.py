import sys

def somaSubtrai(operacoes):
    totalsum = 0
    stemp = ""
    last_operator = "+"
    for i in range(len(operacoes)):
        w=operacoes[i]
        if w not in ["+", "-"]:
            stemp = stemp + w
        if w in ["+", "-"] or i==len(operacoes)-1:
            
            if last_operator == "+":
                totalsum += int(stemp)
            elif last_operator == "-":
                totalsum -= int(stemp)
            last_operator = w
            stemp = ""
    print(totalsum)

args = sys.argv[1:][0]
somaSubtrai(args)