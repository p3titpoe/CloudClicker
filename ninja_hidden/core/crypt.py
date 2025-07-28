import random
import os
import json
import string
from pathlib import Path
from .objs import KeyGenerators
from dataclasses import dataclass
from cryptography.fernet import Fernet

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

def _randomize(split:str|list,force_nmbr:int = None)->dict:
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
    # print(len("".join(new_k)))
    return {'passkey':passphrase,'key':"".join(new_k)}

def _randomize2(mtrx:dict, token:str, control:list=None)->dict:
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

def _fingerprinting(fingerprint:list[int])->list:
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

def _randomize2_n(token:str,passphrase:list)->dict:
    token = list(token)

    new_passphrase = [str(x) if x >= 10 else f"{KeyGenerators.text('alpha',1)}{x}" for x in passphrase]
    new_token = [f'{x}{KeyGenerators.text('alpha',1)}' for x in token]
    new_token.extend(new_passphrase)
    fingerprint = []
    conv = ['a','b','']
    res =_randomize(new_token)
    fingerprint = _fingerprinting(res['passkey'])
    # fingerprint = [str(x) if x >= 26 else f"{KeyGenerators.text('all',1)}{KeyGenerators.char_by_idx('alpha',x)}" for x in
    #                   res['passkey']]
    gg = ''.join([str(x) for x in res['passkey']])
    # print('og passkes ::: ',res['passkey'])
    # print('og passkes list len ::: ',len(res['passkey']))
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
                # print(f"Alpha Up: IDX: {idx}  Number: {idx}  Control:{ct}   finger:{ct2}   chunk: {chunk}")
            if scnd.islower():
                ll = KeyGenerators.char_lists('lower')[0]
                idx = ll.index(scnd)
                out.append(idx+52)
                # print(f"Alphs Lo: IDX: {idx}  Number: {idx+52}  Control:{ct}   finger:{ct2}   chunk: {chunk}")

        elif first.isdigit():
            ll = KeyGenerators.char_lists('upper')[0]
            idx = ll.index(scnd)
            out.append(idx + 26)
            # print(f"Digit Up: IDX: {idx}  Number: {idx+26}  Control:{ct}   finger:{ct2}    chunk: {chunk}")

        elif first in list(string.punctuation):
            ll = KeyGenerators.char_lists('lower')[0]
            idx = ll.index(scnd)
            out.append(idx + 78)
            # print(f"Punct Lo: IDX: {idx}  Number: {idx}  Control:{ct}   finger:{ct2}    chunk: {chunk}")
        else:
            print(f"None:  imput: {first} {scnd}  Control:{ct}   finger:{ct2}    chunk: {chunk}")
        x = x+2
    return out

def _randomize3(passkey:dict,key:str):
    chk = passkey[3]
    key = list(key)
    objlen = len(chk)
    keylen = len(key)
    tocheck = {}
    out = ""
    step = 1
    if objlen == keylen:
        for i in range(0,objlen,step):
            char = key[i:i+step]
            # print(char)
            tocheck[chk[i]] = char
    #
        order = sorted(tocheck)

        for x in order:
            out += tocheck[x][0]
    return bytes(out,'utf-8')

def _randomize4():
    pass

########################################################################################################################
# Maker & Userclasses
########################################################################################################################
@dataclass(repr=False)
class KyMaker:
    """Generate the ingredients for the """
    _mtrx:dict[int:str]
    _mstrk:bytes = None
    _token1:str = None
    _token2:str = None
    _phases:dict[int:list] = None

    def __post_init__(self):
        self._mstrk = KeyGenerators.key()
        self._phases = {}
        self._token1 = KeyGenerators.sha256(self._mstrk)
        l1ky = _randomize(self._mstrk.decode(),1)
        self._phases[3] = l1ky['passkey']
        self._token2 = KeyGenerators.sha256(bytes(l1ky['key'],'utf-8'))
        self._scnd = l1ky['key']
        self._recon()

    def _display(self)->str:
        out = ""
        for k, d in self.__dict__.items():
            if 'mstrk' in k or 'scnd' in k:
                pass
            elif 'phases' in k:
                for n in range(1,len(self._phases)+1):
                    v = self._phases[n]
                    out += f"{k[1:]}{n}  :: {v}  :: {len(v)}\n"
            elif 'mtrx' in k:
                pass
                # tx = "\n".join([v for j, v in d.items()])
                # out += f"{k[1:]} :: {tx}\n"
            else:
                out += f"{k[1:]} :: {d}\n "
        return out

    def __repr__(self)->str:
        tx = self._display()
        return tx

    def _recombine(self,first:list,scnd:list)->list:
        out = [(v,scnd[i]) for i,v in enumerate(first)]
        return out

    def _recon(self,w:int = 80,h:int = 44)->None:
        if self._mtrx is None:
            self._mtrx = KeyGenerators.matrix(w,h)
        res = _randomize2(self._mtrx,self._scnd)
        self._phases[1] = [v[0] for v in res['passkey']]
        self._phases[2] = [v[1] for v in res['passkey']]
        self._mtrx = res['mtrx']

    def _rochade(self):
        pass

    def store(self,pth:Path = None):
        if pth is None:
            p = os.path.abspath(__file__)
            pth = Path(p)
        wkdir = pth.parent
        with open(f"{wkdir}/ky.pub","w") as fh:
            tx = "\n".join([v for j, v in self._mtrx.items()])
            fh.write(tx)


        # print(pth.parent)
        # print(p)


@dataclass(init=False)
class KyUser:
    _token:str
    _phase:dict
    _scnd:str

    def __init__(self, inp:KyMaker):
        self._token = inp._token1
        self._phase = inp._phases
        self._scnd = inp._scnd
        # print(inp._mstrk)

    def _check_key(self)->bytes:
        res = _randomize3(self._phase,self._scnd)
        if KeyGenerators.sha256(res) == self._token:
            return res

    def _load_key(self)->Fernet:
        return Fernet(self._check_key())

    def encode(self, val:bytes)->str:
        k = self._load_key()
        out = k.encrypt(val)
        return out.decode()

    def decode(self,val:str)->str:
        k = self._load_key()
        out = k.decrypt(val)
        return out.decode()


@dataclass
class KyCombinator:
    _k1:KyMaker = None
    _k2:KyMaker = None
    _mtrx:dict[int:str] = None

    def __post_init__(self):
        self._mtrx = KeyGenerators.matrix(44,44)
        self._k1 = KyMaker(self._mtrx)
        self._k2 = KyMaker(self._mtrx)
        # print(self._k2._mstrk)
        # self._combine()

    def _combine(self)->KyUser:
        kyusr2 = KyUser(self._k2)
        tt ={'syssecret':self._k1._mstrk.decode(),
             'syssec':self._k1._scnd,
             # 'phases':json.dumps(self._k1._phases)}
             'phases':self._k1._phases}

        ttjs = json.dumps(tt)
        print(ttjs)
        return kyusr2

