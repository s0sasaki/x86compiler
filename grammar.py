
BNF = [("_PROG",      ["_STMT"]),
       ("_STMT",      ["_BLOCK"]),
       ("_STMT",      ["_ASSIGN", ";"]),
       ("_STMT",      ["_IF"]),
       ("_STMT",      ["_WHILE"]),
       ("_STMT",      ["_CALLPROC", ";"]),
       ("_STMT",      ["_TAILCALL", ";"]),
       ("_BLOCK",     ["{", "_DECS", "_STMTS", "}"]),
       ("_BLOCK",     ["{", "_STMTS", "}"]),
       ("_DECS",      ["_VARDEC"]),
       ("_DECS",      ["_FUNCDEC"]),
       ("_DECS",      ["_DECS", "_VARDEC"]),
       ("_DECS",      ["_DECS", "_FUNCDEC"]),
       ("_VARDEC",    ["_INTTYP", ";"]),
       ("_VARDEC",    ["_ARRAYTYP", ";"]),
       ("_INTTYP",    ["int", "_ALPHABET"]),
       ("_ARRAYTYP",  ["_INTTYP", "[", "_INTEXP", "]"]),
       ("_FUNCDEC",   ["_INTTYP", "(", "_ARGDECS", ")", "_STMT"]),
       ("_FUNCDEC",   ["_INTTYP", "(", ")", "_STMT"]), 
       ("_ARGDECS",   ["_ARGDEC"]),
       ("_ARGDECS",   ["_ARGDECS", ",", "_ARGDEC"]),
       ("_ARGDEC",    ["_INTTYP"]),
       ("_STMTS",     ["_STMT"]),
       ("_STMTS",     ["_STMTS", "_STMT"]),
       ("_ASSIGN",    ["_VAR", "=", "_EXPR"]),
       ("_ASSIGN",    ["_INDEXEDVAR", "=", "_EXPR"]),
       ("_VAR",       ["_ALPHABET"]),
       ("_INDEXEDVAR",["_VAR", "[", "_EXPR", "]"]),
       ("_EXPR",      ["_EXPR", "+", "_TERM"]),
       ("_EXPR",      ["_EXPR", "-", "_TERM"]),
       ("_EXPR",      ["_TERM"]),
       ("_TERM",      ["_TERM", "*", "_FACTOR"]),
       ("_TERM",      ["_TERM", "/", "_FACTOR"]),
       ("_TERM",      ["_FACTOR"]),
       ("_FACTOR",    ["(", "_EXPR", ")"]),
       ("_FACTOR",    ["_VAREXP"]),
       ("_FACTOR",    ["_INTEXP"]),
       ("_FACTOR",    ["_CALLFUNC"]),
       ("_VAREXP",    ["_VAR"]),
       ("_VAREXP",    ["_INDEXEDVAR"]),
       ("_INTEXP",    ["_NUMBER"]),
       ("_IF",        ["if", "(", "_COND", ")", "_STMT", "end"]),
       ("_IF",        ["if", "(", "_COND", ")", "_STMT", "else", "_STMT", "end"]),
       ("_WHILE",     ["while", "(", "_COND", ")", "_STMT", "end"]),
       ("_COND",      ["_EXPR", "<",  "_EXPR"]),
       ("_COND",      ["_EXPR", "<=", "_EXPR"]),
       ("_COND",      ["_EXPR", ">",  "_EXPR"]),
       ("_COND",      ["_EXPR", ">=", "_EXPR"]),
       ("_COND",      ["_EXPR", "==", "_EXPR"]),
       ("_COND",      ["_EXPR", "!=", "_EXPR"]),
       ("_CALLFUNC",  ["_FUNCNAME", "(", "_ARGS", ")"]),
       ("_CALLFUNC",  ["_FUNCNAME", "(", ")"]), 
       ("_FUNCNAME",  ["_ALPHABET"]),
       ("_CALLPROC",  ["iprint", "(", "_EXPR", ")"]),
       ("_CALLPROC",  ["return", "_EXPR"]),
       ("_CALLPROC",  ["_FUNCNAME", "(", "_ARGS", ")"]),
       ("_CALLPROC",  ["_FUNCNAME", "(", ")"]), 
       ("_ARGS",      ["_ARG"]),
       ("_ARGS",      ["_ARGS", ",", "_ARG"]),
       ("_ARG",       ["_EXPR"]),
       ("_TAILCALL",  ["tailcall", "_CALLPROC"])]

NONTERMINAL = list(set([i[0] for i in BNF]))
TERMINAL = list(set([j for i in BNF for j in i[1]]) - set(NONTERMINAL) | set(["$"]))
SYMBOL = TERMINAL + NONTERMINAL

