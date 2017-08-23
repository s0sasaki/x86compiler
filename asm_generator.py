import copy

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

maincode = []
subcode  = []
label = 0

def make_var(typ, nest, offset):
    return {"typ":typ, "nest":nest, "offset":offset}

def make_func(typ, nest, arg):
    return {"typ":typ, "nest":nest, "arg":arg}

def trans_decs(ast_decs, nest, top_offset, env, code, delta_offset):
    assert(ast_decs[0] == "_DECS")
    if ast_decs[1][0] == "_DECS":
        delta_offset = trans_decs(ast_decs[1], nest, top_offset, env, code, delta_offset)
        if ast_decs[2][0] == "_VARDEC":
            delta_offset = trans_vardec(ast_decs[2], nest, top_offset, env, code, delta_offset)
        elif ast_decs[2][0] == "_FUNCDEC":
            trans_funcdec(ast_decs[2], nest, top_offset, env, code, delta_offset)
    elif ast_decs[1][0] == "_VARDEC":
        delta_offset = trans_vardec(ast_decs[1], nest, top_offset, env, code, delta_offset)
    elif ast_decs[1][0] == "_FUNCDEC":
        trans_funcdec(ast_decs[1], nest, top_offset, env, code, delta_offset)
    return delta_offset

def trans_vardec(ast_vardec, nest, top_offset, env, code, delta_offset):
    assert(ast_vardec[0] == "_VARDEC")
    if ast_vardec[1][0] == "_INTTYP":
        return trans_inttyp(ast_vardec[1], nest, top_offset, env, code, delta_offset)
    elif ast_vardec[1][0] == "_ARRAYTYP":
        return trans_arraytyp(ast_vardec[1], nest, top_offset, env, code, delta_offset)

def trans_inttyp(ast_inttyp, nest, top_offset, env, code, delta_offset):
    assert(ast_inttyp[0] == "_INTTYP")
    delta_offset -= 8
    env[ast_inttyp[1]] = make_var(ast_inttyp[0], nest, top_offset + delta_offset)
    return delta_offset

def trans_arraytyp(ast_arraytyp, nest, top_offset, env, code, delta_offset):
    assert(ast_arraytyp[0] == "_ARRAYTYP")
    assert(ast_arraytyp[1][0] == "_INTTYP")
    assert(ast_arraytyp[2][0] == "_INTEXP")
    delta_offset -= 8
    env[ast_arraytyp[1][1]] = make_var(ast_arraytyp[1][0], nest, top_offset + delta_offset)
    delta_offset -= 8*(int(ast_arraytyp[2][1])-1)
    return delta_offset

def trans_funcdec(ast_funcdec, nest, top_offset, env, code, delta_offset):
    assert(ast_funcdec[0] == "_FUNCDEC")
    assert(ast_funcdec[1][0] == "_INTTYP")
    if len(ast_funcdec)==3:
        env[ast_funcdec[1][1]] = make_func(ast_funcdec[1][0], nest+1, None)
    elif len(ast_funcdec)==4:
        env[ast_funcdec[1][1]] = make_func(ast_funcdec[1][0], nest+1, ast_funcdec[2])
        trans_argdecs(ast_funcdec[2], nest+1, top_offset, env, code, delta_offset)
    tmpcode = []
    tmpcode.append(ast_funcdec[1][1]+":")
    tmpcode.extend(prologue)
    tmpcode.append(ast_funcdec[1][1]+"_REC:") # for tailcall
    if len(ast_funcdec)==3:
        trans_stmt(ast_funcdec[2], nest+1, 0, env, tmpcode) 
    elif len(ast_funcdec)==4:
        trans_stmt(ast_funcdec[3], nest+1, 0, env, tmpcode) 
    tmpcode.extend(epilogue)
    subcode.extend(tmpcode)

def trans_argdecs(ast_argdecs, nest, top_offset, env, code, delta_offset):
    assert(ast_argdecs[0] == "_ARGDECS")
    if ast_argdecs[1][0] == "_ARGDECS":
        arg_offset = trans_argdecs(ast_argdecs[1], nest, top_offset, env, code, delta_offset)
        trans_argdec(ast_argdecs[2], nest, top_offset, env, code, delta_offset, arg_offset)
    elif ast_argdecs[1][0] == "_ARGDEC":
        arg_offset = 24
        trans_argdec(ast_argdecs[1], nest, top_offset, env, code, delta_offset, arg_offset)
    return arg_offset + 8

def trans_argdec(ast_argdec, nest, top_offset, env, code, delta_offset, arg_offset):
    assert(ast_argdec[0]=="_ARGDEC")
    assert(ast_argdec[1][0]=="_INTTYP")
    env[ast_argdec[1][1]] = make_var(ast_argdec[1][0], nest, arg_offset) 

def trans_exp(ast_exp, nest, top_offset, env, code): 
    if ast_exp[0]=="_INTEXP":
        code.append("\tpushq $"+ast_exp[1])
    elif ast_exp[0]=="_VAREXP":
        trans_var(ast_exp[1], nest, top_offset, env, code)
        code.append("\tmovq (%rax), %rax")
        code.append("\tpushq %rax")
    elif ast_exp[0]=="_CALLFUNC":
        if ast_exp[1]=="+":
            trans_exp(ast_exp[2], nest, top_offset, env, code)
            trans_exp(ast_exp[3], nest, top_offset, env, code)
            code.append("\tpopq %rax")
            code.append("\taddq %rax, (%rsp)")
        elif ast_exp[1]=="-":
            trans_exp(ast_exp[2], nest, top_offset, env, code)
            trans_exp(ast_exp[3], nest, top_offset, env, code)
            code.append("\tpopq %rax")
            code.append("\tsubq %rax, (%rsp)")
        elif ast_exp[1]=="*":
            trans_exp(ast_exp[2], nest, top_offset, env, code)
            trans_exp(ast_exp[3], nest, top_offset, env, code)
            code.append("\tpopq %rax")
            code.append("\timulq (%rsp), %rax")
            code.append("\tmovq %rax, (%rsp)")
        elif ast_exp[1]=="/":
            trans_exp(ast_exp[2], nest, top_offset, env, code)
            trans_exp(ast_exp[3], nest, top_offset, env, code)
            code.append("\tpopq %rbx")
            code.append("\tpopq %rax")
            code.append("\tcqto")
            code.append("\tidivq %rbx")
            code.append("\tpushq %rax")
        else:
            ast_proc = ["_CALLPROC", ast_exp[1], ast_exp[2]]
            trans_callproc(ast_proc, nest, top_offset, env, code)
            code.append("\tpushq %rax")

def trans_var(ast_var, nest, top_offset, env, code):
    if ast_var[0]=="_VAR":
        offset = str(env[ast_var[1]]["offset"])
        code.append("\tmovq %rbp, %rax")
        for i in range(nest - env[ast_var[1]]["nest"]):  
            code.append("\tmovq 16(%rax), %rax")        
        code.append("\tleaq "+offset+"(%rax), %rax")
    elif ast_var[0]=="_INDEXEDVAR":
        trans_exp(["_CALLFUNC", "*", ["_INTEXP", "-8"], ast_var[2]], nest, top_offset, env, code)
        trans_var(ast_var[1], nest, top_offset, env, code)
        code.append("\tpopq %rbx")
        code.append("\tleaq (%rax,%rbx), %rax")

def trans_cond(ast_exp, nest, top_offset, env, code): 
    global label
    if ast_exp[0]=="_COND":
        trans_exp(ast_exp[2], nest, top_offset, env, code)
        trans_exp(ast_exp[3], nest, top_offset, env, code)
        code.append("\tpopq %rax")
        code.append("\tpopq %rbx")
        code.append("\tcmpq %rax, %rbx")
        label = label+1
        if   ast_exp[1]=="==": code.append("\tjne L"+str(label))
        elif ast_exp[1]=="!=": code.append("\tje  L"+str(label))
        elif ast_exp[1]==">":  code.append("\tjle L"+str(label))
        elif ast_exp[1]==">=": code.append("\tjl  L"+str(label))
        elif ast_exp[1]=="<":  code.append("\tjge L"+str(label))
        elif ast_exp[1]=="<=": code.append("\tjg  L"+str(label))

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
    assert(ast_stmts[0] == "_STMTS")
    if ast_stmts[1][0] == "_STMTS":
        trans_stmts(ast_stmts[1], nest, top_offset, env, code)
        trans_stmt( ast_stmts[2], nest, top_offset, env, code)
    elif ast_stmts[1][0] == "_STMT":
        trans_stmt( ast_stmts[1], nest, top_offset, env, code)

def trans_stmt(ast_stmt, nest, top_offset, env, code):
    assert(ast_stmt[0] == "_STMT")
    if ast_stmt[1][0] == "_ASSIGN":
        trans_assign(ast_stmt[1], nest, top_offset, env, code)
    elif ast_stmt[1][0] == "_BLOCK":
        trans_block(ast_stmt[1], nest, top_offset, env, code)
    elif ast_stmt[1][0] == "_IF":
        trans_if(ast_stmt[1], nest, top_offset, env, code)
    elif ast_stmt[1][0] == "_WHILE":
        trans_while(ast_stmt[1], nest, top_offset, env, code)
    elif ast_stmt[1][0] == "_CALLPROC":
        trans_callproc(ast_stmt[1], nest, top_offset, env, code)
    elif ast_stmt[1][0] == "_TAILCALL":
        trans_tailcall(ast_stmt[1], nest, top_offset, env, code)

def trans_assign(ast_assign, nest, top_offset, env, code):
    assert(ast_assign[0] == "_ASSIGN")
    trans_exp(ast_assign[2], nest, top_offset, env, code)
    trans_var(ast_assign[1], nest, top_offset, env, code)
    code.append("\tpopq (%rax)")

def trans_block(ast_block, nest, top_offset, env, code):
    assert(ast_block[0] == "_BLOCK")
    local_env = copy.deepcopy(env)
    if len(ast_block) == 3:
        delta_offset = trans_decs(ast_block[1], nest, top_offset, local_env, code, 0)
        code.append("\tsubq $"+str(int((-delta_offset+8)/16)*16)+", %rsp")
        trans_stmts(ast_block[2], nest, top_offset+delta_offset, local_env, code)
        code.append("\taddq $"+str(int((-delta_offset+8)/16)*16)+", %rsp")
    else:
        trans_stmts(ast_block[1], nest, top_offset, local_env, code)

def trans_if(ast_if, nest, top_offset, env, code):
    assert(ast_if[0] == "_IF")
    global label
    if len(ast_if) == 3:
        trans_cond(ast_if[1], nest, top_offset, env, code)
        savelabel = label
        trans_stmt(ast_if[2], nest, top_offset, env, code)
        code.append("L"+str(savelabel)+":")
    else:
        trans_cond(ast_if[1], nest, top_offset, env, code)
        oldlabel = label
        label    = label+1
        newlabel = label
        trans_stmt(ast_if[2], nest, top_offset, env, code)
        code.append("\tjmp L"+str(newlabel))
        code.append("L"+str(oldlabel)+":")
        trans_stmt(ast_if[3], nest, top_offset, env, code)
        code.append("L"+str(newlabel)+":")

def trans_while(ast_while, nest, top_offset, env, code):
    assert(ast_while[0] == "_WHILE")
    global label
    newlabel = label+2
    code.append("L"+str(newlabel)+":")
    trans_cond(ast_while[1], nest, top_offset, env, code)
    oldlabel = label
    label    = label+1
    trans_stmt(ast_while[2], nest, top_offset, env, code)
    code.append("\tjmp L"+str(newlabel))
    code.append("L"+str(oldlabel)+":")

def trans_callproc(ast_callproc, nest, top_offset, env, code):
    assert(ast_callproc[0] == "_CALLPROC")
    if ast_callproc[1] == "iprint":
        trans_exp(ast_callproc[2], nest, top_offset, env, code)
        code.append("\tpopq  %rsi")
        code.append("\tleaq IO(%rip), %rdi")
        code.append("\tmovq $0, %rax")
        code.append("\tcallq printf")
    elif ast_callproc[1] == "return":
        trans_exp(ast_callproc[2], nest, top_offset, env, code)
        code.append("\tpopq  %rax")
        code.extend(epilogue)
    else:
        args = ast_callproc[2] if len(ast_callproc)==3 else []
        arglength = count_args(args)
        if arglength%2 == 0:
            code.append("\tpushq $0")
        trans_args(args, nest, top_offset, env, code)
        passlink(nest, env[ast_callproc[1][1]]["nest"], code)    
        code.append("\tcallq "+ast_callproc[1][1])
        code.append("\taddq $"+str((arglength+1+1)//2*2*8)+", %rsp")

def count_args(args):
    if args == [] or args[0]=="_ARG":
        return 0
    elif args[0]=="_ARGS":
        return 1+count_args(args[1])

def trans_args(args, nest, top_offset, env, code):
    if args == []:
        return
    elif args[1][0] == "_ARGS":
        trans_arg( args[2], nest, top_offset, env, code)
        trans_args(args[1], nest, top_offset, env, code)
    elif args[1][0] == "_ARG":
        trans_arg( args[1], nest, top_offset, env, code)

def trans_arg(arg, nest, top_offset, env, code):
    assert(arg[0] == "_ARG")
    trans_exp(arg[1], nest, top_offset, env, code)

def trans_tailcall(ast_tailcall, nest, top_offset, env, code):
    assert(ast_tailcall[0] == "_TAILCALL")
    assert(ast_tailcall[1][0] == "_CALLPROC")
    args = ast_tailcall[1][2] if len(ast_tailcall[1])==3 else []
    arglength = count_args(args)
    trans_args(args, nest, top_offset, env, code)
    for i in range(arglength):
        code.append("\tmovq %rbp, %rax")
        code.append("\tpopq "+str(24 + i*8)+"(%rax)")
    code.append("\tjmp "+ast_tailcall[1][1][1]+"_REC")

def asm_generator(ast):
    nest       = 0
    top_offset = 0
    global_env = {}
    maincode.extend(io)
    maincode.extend(header)
    trans_stmt(ast, nest, top_offset, global_env, maincode)
    maincode.extend(epilogue)
    return maincode + subcode


