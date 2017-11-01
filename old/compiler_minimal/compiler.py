import sys

def tokenize(s):
    return s.replace("("," ( ").replace(")"," ) ").split()

def parse(tokens):
    token = tokens.pop(0)
    if token == "(":
        L = []
        while tokens[0] != ")":
            L.append(parse(tokens))
        tokens.pop(0)
        return L
    elif token == ")":
        raise SyntaxError("unexpected )")
    else:
        return token

def make_var(typ, level, offset):
    return {"typ":typ, "level":level, "offset":offset}

def decs(ast_decs):
    assert(ast_decs[0] == "DECS")
    offset = 0
    for i in range(1, len(ast_decs)):
        assert(ast_decs[i][0] == "VARDEC")
        offset -= 8
        regvars[ast_decs[i][1][1]] = make_var(ast_decs[i][1][0], 0, offset)
    print("\tsubq $"+str(int((-offset+8)/16)*16)+", %rsp")

def trans_exp(ast_exp):
    if ast_exp[0]=="INTEXP":
        print("\tpushq $"+ast_exp[1])
    elif ast_exp[0]=="VAREXP":
        trans_var(ast_exp[1])
        print("\tmovq (%rax), %rax")
        print("\tpushq %rax")
    elif ast_exp[0]=="CALLFUNC":
        if ast_exp[1][0]=="+":
            trans_exp(ast_exp[1][1])
            trans_exp(ast_exp[1][2])
            print("\tpopq %rax")
            print("\taddq %rax, (%rsp)")
        elif ast_exp[1][0]=="-":
            trans_exp(ast_exp[1][1])
            trans_exp(ast_exp[1][2])
            print("\tpopq %rax")
            print("\tsubq %rax, (%rsp)")
        elif ast_exp[1][0]=="*":
            trans_exp(ast_exp[1][1])
            trans_exp(ast_exp[1][2])
            print("\tpopq %rax")
            print("\timulq (%rsp), %rax")
            print("\tmovq %rax, (%rsp)")
        elif ast_exp[1][0]=="/":
            trans_exp(ast_exp[1][1])
            trans_exp(ast_exp[1][2])
            print("\tpopq %rbx")
            print("\tpopq %rax")
            print("\tcqto")
            print("\tidivq %rbx")
            print("\tpushq %rax")

def trans_var(ast_var):
    assert(ast_var[0]=="VAR")
    offset = str(regvars[ast_var[1]]["offset"])
    print("\tmovq %rbp, %rax")
    print("\tleaq "+offset+"(%rax), %rax")

def emit(ast_stmts):
    assert(ast_stmts[0] == "STMTS")
    for i in range(1, len(ast_stmts)):
        if ast_stmts[i][0] == "ASSIGN":
            trans_exp(ast_stmts[i][2])
            trans_var(ast_stmts[i][1])
            print("\tpopq (%rax)")
        elif ast_stmts[i][0] == "CALLPROC":
            if ast_stmts[i][1] == "iprint":
                trans_exp(ast_stmts[i][2])
                print("\tpopq  %rsi")
                print("\tleaq IO(%rip), %rdi")
                print("\tmovq $0, %rax")
                print("\tcallq printf")

io       = "IO:\n"                \
         + "\t.string \"%lld\"\n" \
         + "\t.text\n"
header   = "\t.globl main\n"      \
         + "main:\n"              \
         + "\tpushq %rbp\n"       \
         + "\tmovq %rsp, %rbp\n"
epilogue = "\tleaveq\n"           \
         + "\tretq\n"         

def compile(ast_blocks):
    assert(ast_blocks[0] == "BLOCK")
    print(io,       end="")
    print(header,   end="")
    decs(ast_blocks[1]) 
    emit(ast_blocks[2]) 
    print(epilogue, end="")

regvars = {}
filename  = sys.argv[1]
with open(filename, "r") as f:
    s = f.read()
ast = parse(tokenize(s))
compile(ast)

