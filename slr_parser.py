from grammar import *
import parser_generator

LR    = parser_generator.parser_generator()
r2n   = [ i[0] for i in BNF ]
pops  = [ len(i[1]) for i in BNF]

def tokenizer(code):
    punctuator = ["$", ";", ",", "+", "-", "*", "/", "(", ")", "{", "}", "[", "]", "=", ">", "<", "!"]
    for i in punctuator:
        code = code.replace(i," "+i+" ")
    for i in ["<=", ">=", "==", "!="]:
        code = code.replace(i[0]+"  "+i[1], i)
    tokens = code.split()
    tokens += "$"
    return tokens

def token_to_symbol(token):
    if token in SYMBOL:
        return token
    elif token.isdigit():
        return "_NUMBER"
    else:
        return "_ALPHABET"

def parser(tokens, debug=False):
    stack = []
    output = []
    ix = 0
    symbol = token_to_symbol(tokens[ix])
    ix += 1
    stack.append(0)
    while True:
        state = stack[-1]
        action = LR[state][symbol]
        if debug:
            token = tokens[ix] if ix < len(tokens) else "-"
            print("tokens[ix]:",token," state:",state, " action:", action,"\t", end="")
        if action == []:
            raise Exception
        elif action[0] == "q":
            if debug: print("OK") 
            break
        elif action[0] == "s":
            stack.append(action[1])
            if debug: print("shift : push ",action, "\t",stack)
            symbol = token_to_symbol(tokens[ix])
            ix += 1
        else:
            stack = stack[:-1*pops[action[1]]]
            state = LR[stack[-1]][r2n[action[1]]]
            if debug: print("reduce: push ",action, "\t",stack)
            output.append(action[1])
            stack.append(state[1])
    return output
