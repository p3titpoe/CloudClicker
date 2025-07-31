import random
import string
from .objs import KeyGenerators

########################################################################################################################
# Obfuscation functions
########################################################################################################################
def _spliterize(tosplit,force_nmbr:int = None)->list:
    rndm =[1,2,4]
    if force_nmbr is not None:
        rndm = [force_nmbr]
    rndm_choice = random.choice(rndm)
    new_order = []
    lastpos = 0
    end = int(len(tosplit)/rndm_choice)
    for i in range(0,end):
        new_order.append(tosplit[lastpos:lastpos+rndm_choice])
        lastpos += rndm_choice
    return new_order

def randomize(split:str|list,force_nmbr:int = None)->dict:
    splitkey = split
    if isinstance(splitkey,str):
        splitkey = _spliterize(split,force_nmbr)

    obj_len = len(splitkey)
    passphrase = []
    obj=[]
    new_obj_len = 0
    while new_obj_len < obj_len:
        ch = random.choice(splitkey)
        if ch is not None:
            idx = splitkey.index(ch)
            obj.append(ch)
            passphrase.append(idx)
            splitkey[idx] = None
            new_obj_len += 1
    new_k = [p for p in obj]
    # print("PASS   ::",passphrase)
    # print("SPLIT  ::",split)
    # print(len("".join(new_k)))
    return {'passkey':passphrase,'key':"".join(new_k)}

def randomize2(mtrx:dict, token:str, control:list=None)->dict:
    grid_x = [x for x in range(0,len(mtrx[0]))]
    grid_y = [x for x in mtrx.keys()]
    ctrl = None if control is None else [x[1] for x in control]

    pkc =[]
    for l in token:
        h = random.choice(grid_y)
        w = 0
        if ctrl is not None and h in ctrl:
            idx = ctrl.index(h)
            valw = control[idx][0]
            w = random.choice(grid_x)
            while w == valw:
                w = random.choice(grid_x)
        else:
            w = random.choice(grid_x)

        if (w,h) not in pkc:
            pkc.append((w,h))
            wed = list(mtrx[h])
            wed[w] = l
            mtrx[h] = "".join(wed)

    return {'passkey':pkc,
            'mtrx':mtrx,
            'key':token}

def fingerprinting(fingerprint:list[int])->list:
    our = []
    for i,fp in enumerate(fingerprint):
        p=""
        if fp < 26:
            p = f"{KeyGenerators.text('alpha',1)}{KeyGenerators.char_by_idx('upper',fp)}"

        elif 26 <= fp <52:
            cnt = fp-26
            p = f"{KeyGenerators.text('digit',1)}{KeyGenerators.char_by_idx('upper',cnt)}"

        elif 52 <= fp < 78:
            cnt = fp-52
            p = f"{KeyGenerators.text('alpha',1)}{KeyGenerators.char_by_idx('lower',cnt)}"

        elif 78 <= fp < 104:
            cnt = fp-78
            p = f"{KeyGenerators.text('punct',1)}{KeyGenerators.char_by_idx('lower',cnt)}"

        else:
            p = str(fp)
        our.append(p)
    return our

def fingerize(token:str, passphrase:list)->dict:
    token = list(token)
    new_passphrase = [str(x) if x >= 10 else f"{KeyGenerators.text('alpha',1)}{x}" for x in passphrase]
    new_token = [f'{x}{KeyGenerators.text('all',1)}' for x in token]
    new_token.extend(new_passphrase)
    fingerprint = []
    res =randomize(new_token,1)
    # print("RANDD :: ",res)
    fingerprint = fingerprinting(res['passkey'])
    return {'fingerprint':"".join(fingerprint),'token':res['key'],'olpass':res['passkey'],'ogfp':fingerprint}

def _urandomize2_n(fingerprint:str,ctrl:list=None,ctrl2:list=None)->list:
    cnt = int(len(fingerprint)/2)
    print(cnt)
    out = []
    x = 0
    while len(out) < cnt:
        chunk = fingerprint[x:x+2]
        first,scnd = list(chunk)

        if first.isalpha():
            if scnd.isupper():
                ll = KeyGenerators.char_lists('upper')[0]
                idx = ll.index(scnd)
                out.append(idx)
            if scnd.islower():
                ll = KeyGenerators.char_lists('lower')[0]
                idx = ll.index(scnd)
                out.append(idx+52)

        elif first.isdigit():
            ll = KeyGenerators.char_lists('upper')[0]
            idx = ll.index(scnd)
            out.append(idx + 26)

        elif first in list(string.punctuation):
            ll = KeyGenerators.char_lists('lower')[0]
            idx = ll.index(scnd)
            out.append(idx + 78)
        else:
            print(f"None:  imput: {first} {scnd}  chunk: {chunk}")
        x = x+2
    return out

def _urandomize2(matrix:dict,fingerprint):
    pass

def _randomize3a(passkey:list,key:str)->bytes:
    chars = list(key)
    out = {}
    k = ""
    for i,p in enumerate(passkey):
        out[p] = key[i]

    sortd = sorted(out)
    for n in sortd:
        k += out[n]
    return bytes(k,'utf-8')

def randomize3(passkey:list,key:str):
    chk = passkey
    objlen = len(chk)
    tocheck = {}
    out = ""
    step = 2
    i = 0
    cnt = 0
    while cnt < objlen:
        char = key[i:i+step]
        # print(char)
        tocheck[chk[cnt]] = char
        cnt += 1
        i+=2
    order = sorted(tocheck)

    for x in order:
        out += tocheck[x]
    return bytes(out,'utf-8')

def _randomize4(key:bytes|str)->dict:
    if isinstance(key,bytes):
        key = key.decode()
    cntlen = int(len(key)/2)
    msb = []
    lsb = []
    i = 0
    cnt = 0
    while cnt < cntlen:
        char = key[i:i+2]
        if cnt < 44:
            msb.append(char[0])
        else:
            if char.isdigit():
                ch = char
            else:
                ch = char[1]
            lsb.append(int(ch))
        cnt += 1
        i+=2
    return {'key':''.join(msb),'passkey':lsb}

def _usr_salt()->str:
    pass