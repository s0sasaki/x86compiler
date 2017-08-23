import sys
import copy

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

def make_var(typ, nest, offset):
    return {"typ":typ, "nest":nest, "offset":offset}

def make_func(typ, nest, arg):
    return {"typ":typ, "nest":nest, "arg":arg}

def trans_decs(ast_decs, nest, top_offset, env, code):
    assert(ast_decs[0] == "DECS")
    delta_offset = 0
    for i in range(1, len(ast_decs)):
        if(ast_decs[i][0] == "FUNCDEC"):
            env[ast_decs[i][1]] = make_func(ast_decs[i][3], nest+1, ast_decs[i][2]) 
            arg_offset = 24
            for j in ast_decs[i][2]:
                env[j[1]] = make_var(j[0], nest+1, arg_offset) 
                arg_offset += 8
            tmpcode = []
            tmpcode.append(ast_decs[i][1]+":")
            tmpcode.extend(prologue)
            tmpcode.append(ast_decs[i][1]+"_REC:") # CALLPROCTAIL
            trans_stmt(ast_decs[i][4], nest+1, 0, env, tmpcode) 
            tmpcode.extend(epilogue)
            subcode.extend(tmpcode)
        elif(ast_decs[i][0] == "VARDEC"):
            if ast_decs[i][1][0] == "INTTYP":
                delta_offset -= 8
                env[ast_decs[i][1][1]] = make_var(ast_decs[i][1][0], nest, top_offset + delta_offset)
            elif ast_decs[i][1][0] == "ARRAYTYP":
                delta_offset -= 8
                env[ast_decs[i][1][3]] = make_var(ast_decs[i][1][2], nest, top_offset + delta_offset)
                delta_offset -= 8*(int(ast_decs[i][1][1])-1)
    return delta_offset

def trans_exp(ast_exp, nest, top_offset, env, code): 
    if ast_exp[0]=="INTEXP":
        code.append("\tpushq $"+ast_exp[1])
    elif ast_exp[0]=="VAREXP":
        trans_var(ast_exp[1], nest, top_offset, env, code)
        code.append("\tmovq (%rax), %rax")
        code.append("\tpushq %rax")
    elif ast_exp[0]=="CALLFUNC":
        if ast_exp[1][0]=="+":
            trans_exp(ast_exp[1][1], nest, top_offset, env, code)
            trans_exp(ast_exp[1][2], nest, top_offset, env, code)
            code.append("\tpopq %rax")
            code.append("\taddq %rax, (%rsp)")
        elif ast_exp[1][0]=="-":
            trans_exp(ast_exp[1][1], nest, top_offset, env, code)
            trans_exp(ast_exp[1][2], nest, top_offset, env, code)
            code.append("\tpopq %rax")
            code.append("\tsubq %rax, (%rsp)")
        elif ast_exp[1][0]=="*":
            trans_exp(ast_exp[1][1], nest, top_offset, env, code)
            trans_exp(ast_exp[1][2], nest, top_offset, env, code)
            code.append("\tpopq %rax")
            code.append("\timulq (%rsp), %rax")
            code.append("\tmovq %rax, (%rsp)")
        elif ast_exp[1][0]=="/":
            trans_exp(ast_exp[1][1], nest, top_offset, env, code)
            trans_exp(ast_exp[1][2], nest, top_offset, env, code)
            code.append("\tpopq %rbx")
            code.append("\tpopq %rax")
            code.append("\tcqto")
            code.append("\tidivq %rbx")
            code.append("\tpushq %rax")
        else:
            ast_proc = ["CALLPROC", ast_exp[1][0], ast_exp[1][1]]
            trans_stmt(ast_proc, nest, top_offset, env, code)
            code.append("\tpushq %rax")

def trans_var(ast_var, nest, top_offset, env, code):
    if ast_var[0]=="VAR":
        offset = str(env[ast_var[1]]["offset"])
        code.append("\tmovq %rbp, %rax")
        for i in range(nest - env[ast_var[1]]["nest"]):  
            code.append("\tmovq 16(%rax), %rax")        
        code.append("\tleaq "+offset+"(%rax), %rax")
    elif ast_var[0]=="INDEXEDVAR":
        trans_exp(["CALLFUNC", ["*", ["INTEXP", "-8"], ast_var[2]]], nest, top_offset, env, code)
        trans_var(ast_var[1], nest, top_offset, env, code)
        #code.append("\tmovq (%rax), %rax")
        code.append("\tpopq %rbx")
        code.append("\tleaq (%rax,%rbx), %rax")

def trans_cond(ast_exp, nest, top_offset, env, code): 
    global label
    if ast_exp[0]=="COND":
        trans_exp(ast_exp[1][1], nest, top_offset, env, code)
        trans_exp(ast_exp[1][2], nest, top_offset, env, code)
        code.append("\tpopq %rax")
        code.append("\tpopq %rbx")
        code.append("\tcmpq %rax, %rbx")
        label = label+1
        if   ast_exp[1][0]=="==": code.append("\tjne L"+str(label))
        elif ast_exp[1][0]=="!=": code.append("\tje  L"+str(label))
        elif ast_exp[1][0]==">":  code.append("\tjle L"+str(label))
        elif ast_exp[1][0]==">=": code.append("\tjl  L"+str(label))
        elif ast_exp[1][0]=="<":  code.append("\tjge L"+str(label))
        elif ast_exp[1][0]=="<=": code.append("\tjg  L"+str(label))


def passlink(src, dst, code):
    if src >= dst:
        deltalevel = src - dst + 1
        code.append("\tmovq %rbp, %rax")
        for i in range(deltalevel):
            code.append("\tmovq 16(%rax), %rax")
        code.append("\tpushq %rax")
    else:
        code.append("\tpushq %rbp")

def trans_stmts(ast_stmts, nest, top_offset, env, code):
    assert(ast_stmts[0] == "STMTS")
    for i in range(1, len(ast_stmts)):
        trans_stmt(ast_stmts[i], nest, top_offset, env, code)

def trans_stmt(ast_stmt, nest, top_offset, env, code):
    global label
    if ast_stmt[0] == "ASSIGN":
        trans_exp(ast_stmt[2], nest, top_offset, env, code)
        trans_var(ast_stmt[1], nest, top_offset, env, code)
        code.append("\tpopq (%rax)")
    elif ast_stmt[0] == "CALLPROC":
        if ast_stmt[1] == "iprint":
            trans_exp(ast_stmt[2], nest, top_offset, env, code)
            code.append("\tpopq  %rsi")
            code.append("\tleaq IO(%rip), %rdi")
            code.append("\tmovq $0, %rax")
            code.append("\tcallq printf")
        elif ast_stmt[1] == "return":
            trans_exp(ast_stmt[2], nest, top_offset, env, code)
            code.append("\tpopq  %rax")
            code.extend(epilogue)
        else:
            if len(ast_stmt[2])%2 == 0:
                code.append("\tpushq $0")
            for i in reversed(ast_stmt[2]):
                trans_exp(i, nest, top_offset, env, code)
            passlink(nest, env[ast_stmt[1]]["nest"], code)    
            code.append("\tcallq "+ast_stmt[1])
            code.append("\taddq $"+str((len(ast_stmt[2])+1+1)//2*2*8)+", %rsp")
    elif ast_stmt[0] == "CALLPROCTAIL":
        arg_offset = 24
        for i in reversed(ast_stmt[2]):
            trans_exp(i, nest, top_offset, env, code)
        for i in ast_stmt[2]:
            code.append("\tmovq %rbp, %rax")
            code.append("\tpopq "+str(arg_offset)+"(%rax)")
            arg_offset += 8
        code.append("\tjmp "+ast_stmt[1]+"_REC")
    elif ast_stmt[0] == "BLOCK":
        local_env = copy.deepcopy(env)
        delta_offset = trans_decs( ast_stmt[1], nest, top_offset, local_env, code)
        code.append("\tsubq $"+str(int((-delta_offset+8)/16)*16)+", %rsp")
        trans_stmts(ast_stmt[2], nest, top_offset+delta_offset, local_env, code)
        code.append("\taddq $"+str(int((-delta_offset+8)/16)*16)+", %rsp")
    elif ast_stmt[0] == "IF":
        if len(ast_stmt)==3:
            trans_cond(ast_stmt[1], nest, top_offset, env, code)
            savelabel = label
            trans_stmt(ast_stmt[2], nest, top_offset, env, code)
            code.append("L"+str(savelabel)+":")
        else:
            assert(ast_stmt[3]=="ELSE")
            trans_cond(ast_stmt[1], nest, top_offset, env, code)
            oldlabel = label
            label    = label+1
            newlabel = label
            trans_stmt(ast_stmt[2], nest, top_offset, env, code)
            code.append("\tjmp L"+str(newlabel))
            code.append("L"+str(oldlabel)+":")
            trans_stmt(ast_stmt[4], nest, top_offset, env, code)
            code.append("L"+str(newlabel)+":")
    elif ast_stmt[0] == "WHILE":
        newlabel = label+2
        code.append("L"+str(newlabel)+":")
        trans_cond(ast_stmt[1], nest, top_offset, env, code)
        oldlabel = label
        label    = label+1
        trans_stmt(ast_stmt[2], nest, top_offset, env, code)
        code.append("\tjmp L"+str(newlabel))
        code.append("L"+str(oldlabel)+":")
        

io       = ["IO:",
            "\t.string \"%lld\"",
            "\t.text"]
header   = ["\t.globl main",
            "main:",
            "\tpushq %rbp",
            "\tmovq %rsp, %rbp"]
prologue = ["\tpushq %rbp",
            "\tmovq %rsp, %rbp"]
epilogue = ["\tleaveq",
            "\tretq"]         
# MEMO: leaveq = "movq %ebp, %esp; popl %ebp"

def compile(ast):
    nest       = 0
    top_offset = 0
    global_env = {}
    maincode.extend(io)
    maincode.extend(header)
    trans_stmt(ast, nest, top_offset, global_env, maincode)
    maincode.extend(epilogue)

maincode = []
subcode  = []
label = 0
filename  = sys.argv[1]
with open(filename, "r") as f:
    s = f.read()
ast = parse(tokenize(s))
compile(ast)

for i in maincode:
    print(i)
for i in subcode:
    print(i)
