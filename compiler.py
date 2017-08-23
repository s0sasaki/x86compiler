import sys
import parser
import asm_generator
import ast_generator

filename = sys.argv[1]
with open(filename, "r") as f:
    code = f.read()

tokens = parser.tokenizer(code)
parser_output = parser.parser(tokens)
ast = ast_generator.ast_generator(parser_output, tokens)
code_asm = asm_generator.asm_generator(ast)

with open("a.s", "w") as f:
    for i in code_asm:
        f.write(i+"\n")

