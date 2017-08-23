import copy
from grammar import *

def make_firstset():
    firstset = {i:set([]) for i in SYMBOL}
    for i in TERMINAL:
        firstset[i].add(i)
    for lhs, rhs in BNF:
        if rhs == []:
            firstset[lhs].add("_EPSIRON")
        elif rhs[0] in TERMINAL:
            firstset[lhs].add(rhs[0])
    flag = True
    while flag:
        flag = False
        for lhs, rhs in BNF:
            for i in rhs:
                tmp = firstset[lhs].union(firstset[i])
                if tmp != firstset[lhs]:
                    firstset[lhs] = tmp
                    flag = True
                if "_EPSIRON" not in firstset[i]:
                    break
    return firstset

def make_followset(firstset):
    followset = {i:set([]) for i in NONTERMINAL}
    followset["_PROG"].add("$")
    flag = True
    while flag:
        flag = False
        for lhs, rhs in BNF:
            for i in range(len(rhs)):
                if rhs[i] in TERMINAL: ###
                    continue           ###
                tmp_followset_i = copy.deepcopy(followset[rhs[i]])
                try:
                    inext = i+1
                    tmp_followset_i |= firstset[rhs[inext]]
                    while "_EPSIRON" in firstset[rhs[inext]]:
                        inext += 1
                        tmp_followset_i |= firstset[rhs[inext]]
                except IndexError:
                    tmp_followset_i |= followset[lhs]
                if tmp_followset_i != followset[rhs[i]]:
                    followset[rhs[i]] = tmp_followset_i
                    flag = True
    return followset

def match_closure(closure_p, closure_q):
    if closure_p["nBNF"] != closure_q["nBNF"]:
        return False
    for i in range(closure_p["nBNF"]):
        if closure_p["BNF"][i] != closure_q["BNF"][i]:
            return False
        if closure_p["dot_position"][i] != closure_q["dot_position"][i]:
            return False
    return True

def make_closure(closure):
    i = 0
    while i < closure["nBNF"]:
        try:
            next_token = BNF[closure["BNF"][i]][1][closure["dot_position"][i]]
        except IndexError:
            continue
        finally:
            i += 1
        if next_token not in TERMINAL:
            for j in range(len(BNF)):
                if next_token != BNF[j][0]:
                    continue
                new_bnf = True
                for l in range(closure["nBNF"]):
                    if closure["BNF"][l]==j and closure["dot_position"][l]==0:
                        new_bnf = False
                if new_bnf:
                    closure["BNF"].append(j)
                    closure["dot_position"].append(0)
                    closure["checked"].append(False)
                    closure["nBNF"] += 1
    return closure

def search_closure(closure, closure_list):
    for i in range(len(closure_list)):
        if match_closure(closure_list[i], closure):
            return i
    return None

def make_network(closure, closure_list):
    for i in range(closure["nBNF"]):
        if closure["checked"][i] or closure["dot_position"][i] >= len(BNF[closure["BNF"][i]][1]):
            continue
        closure["checked"][i] = True
        token = BNF[closure["BNF"][i]][1][closure["dot_position"][i]]
        new_closure = {}
        new_closure["BNF"]          = [closure["BNF"][i]]
        new_closure["dot_position"] = [closure["dot_position"][i]+1]
        new_closure["checked"]      = [False]
        new_closure["nBNF"]         = 1
        new_closure["token"]        = token
        new_closure["next_closure"] = []
        for j in range(i+1, closure["nBNF"]):
            if closure["checked"][j] or closure["dot_position"][j] >= len(BNF[closure["BNF"][j]][1]):
                continue
            if BNF[closure["BNF"][j]][1][closure["dot_position"][j]] == token:
                closure["checked"][j] = True
                new_closure["BNF"].append(closure["BNF"][j])
                new_closure["dot_position"].append(closure["dot_position"][j]+1)
                new_closure["checked"].append(False)
                new_closure["nBNF"] += 1
        new_closure = make_closure(new_closure)
        same_closure_ix = search_closure(new_closure, closure_list)
        if same_closure_ix == None:
            new_closure_ix = len(closure_list)
            closure["next_closure"].append(new_closure_ix)
            closure_list.append(new_closure)
            closure_list = make_network(new_closure, closure_list)
        else:
            closure["next_closure"].append(same_closure_ix)
    return closure_list            

def make_table(closure_list, followset):
    table = [{ i:[] for i in SYMBOL} for _ in closure_list]
    for i in range(len(closure_list)):
        for j in closure_list[i]["next_closure"]:
            table[i][closure_list[j]["token"]].append("s")
            table[i][closure_list[j]["token"]].append(j)
    for i in range(len(closure_list)):
        for j in range(closure_list[i]["nBNF"]):
            lhs = BNF[closure_list[i]["BNF"][j]][0]
            rhs = BNF[closure_list[i]["BNF"][j]][1]
            if len(rhs) != closure_list[i]["dot_position"][j]:
                continue
            for k in followset[lhs]:
                if lhs == "_PROG":
                    table[i][k].append("q")
                else:
                    table[i][k].append("r")
                    table[i][k].append(closure_list[i]["BNF"][j])
    for i in table:
        for k,v in i.items():
            assert(len(v)<3) # SLR Grammar conflict!
    return table

def parser_generator():
    firstset = make_firstset()
    followset = make_followset(firstset)
    topclosure = {"nBNF":         1,
                  "BNF":          [0],
                  "dot_position": [0],
                  "checked":      [False],
                  "token":        None,
                  "next_closure": []}
    topclosure = make_closure(topclosure)
    closure_list = make_network(topclosure, [topclosure])
    return make_table(closure_list, followset)

