import sys
from grammar import *
import parser

def ast_generator(parser_output, tokens):
    if parser_output == []: return 
    r = parser_output.pop()
    if BNF[r][0] in ["_EXPR", "_TERM"]:
        if len(BNF[r][1]) == 1:
            return ast_generator(parser_output, tokens)
        else:
            parent = ["_CALLFUNC", BNF[r][1][1]]
            children = [ast_generator(parser_output, tokens)]
            children = [ast_generator(parser_output, tokens)] + children
            return parent + children
    elif BNF[r][0] == "_FACTOR":
        return ast_generator(parser_output, tokens)
    elif BNF[r][0] == "_COND":
        parent = ["_COND", BNF[r][1][1]]
        children = [ast_generator(parser_output, tokens)]
        children = [ast_generator(parser_output, tokens)] + children
        return parent + children
    else:
        parent = [BNF[r][0]]
        if BNF[r][0] == "_CALLPROC" and BNF[r][1][0] != "_FUNCNAME":
            parent += [BNF[r][1][0]]
        children = []
        for i in BNF[r][1]:
            if i in ["_NUMBER", "_ALPHABET"]:
                identifier = tokens.pop()
                while identifier in TERMINAL:
                    identifier = tokens.pop()
                children = [identifier] + children
            elif i in NONTERMINAL:
                children = [ast_generator(parser_output, tokens)] + children
        return parent + children


