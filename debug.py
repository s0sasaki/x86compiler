# For parsing a manually written AST.

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

