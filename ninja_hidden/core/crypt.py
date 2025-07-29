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
    # print("PASS   ::",passphrase)
    # print("SPLIT  ::",split)
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
    new_token = [f'{x}{KeyGenerators.text('all',1)}' for x in token]
    new_token.extend(new_passphrase)
    fingerprint = []
    res =_randomize(new_token,1)
    # print("RANDD :: ",res)
    fingerprint = _fingerprinting(res['passkey'])
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

def _randomize3(passkey:list,key:str):
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

########################################################################################################################
# Maker & Userclasses
########################################################################################################################
@dataclass(repr=False)
class KyMakerOLD:
    """Generate the ingredients for the """
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

@dataclass(repr=False)
class KyMakerBase:
    user:str
    pwd:str
    salt:str = None
    _saltuser = None
    _k:bytes = None
    _result:dict = None
    _is_printed:bool = False

    def __post_init__(self):
        if isinstance(self.user,bytes):
            raise ValueError(f'Wrong type for user .> needs email str')

        if not len(self.user.split('@')[1].split('.')) > 1:
            raise ValueError(f'Wrong type for user .> needs email')

        self._result = {}

        if self.salt is None:
            self.salt = KeyGenerators.text('all', 22)

        if self._saltuser is None:
            self._saltuser = KeyGenerators.text('all',22)

        if self._k is None:
            user,rest = self.user.split('@')
            tld = rest.split('.')[1]

            token_skel = f"{user}@{self.pwd}@{tld}"
            ky = KeyGenerators.key_from_string(token_skel,bytes(self.salt,'utf-8'))
            self._k = ky

        # self.generate()

    def generate(self):
        pass


@dataclass(repr=False)
class KyMakerSystem(KyMakerBase):

    def __repr__(self):
        atx = (f"KEY     :: {self._k.decode()}\n"
              f"SALT    :: {self.salt}\n"
              f"Finger  :: {self._fp['fingerprint']}\n"
              f"MATRIX  ::\n"
              f"{'\n'.join([v for k,v in self._mtrx.items()])}")
        ttx = "Informations have altready been provided."
        tx=atx
        if self._is_printed:
            tx = ttx
        return tx

    def generate(self)->dict:
        #First iteration
        randdm = _randomize(self._k.decode(),1)
        fp = _randomize2_n(randdm['key'],randdm['passkey'])
        self._fp = fp

        #Second iteration
        mtrx = KeyGenerators.matrix(44,44)
        mtrx_sig = _randomize2(mtrx,self._k.decode())
        self._mtrx = mtrx_sig['mtrx']
        #Prepare the sig for encoding
        prep = {k:None for k in range(0,11)}
        for p in mtrx_sig['passkey']:
            for i,n in enumerate(p):
                ch =""
                if prep[i] is None:
                    prep[i] = []
                ch = n
                prep[i].append(ch)

        msb_fp = _fingerprinting(prep[0])
        msb = "".join(msb_fp)
        lsb_fp = _fingerprinting(prep[1])
        lsb = "".join(lsb_fp)
        sfx= " "
        mtrx_enc = f"{msb}{sfx}{lsb}"
        mtrx_enc = bytes(mtrx_enc,'utf-8')

        #Encode the mtrx res
        f_ky = Fernet(self._k)
        encoded = f_ky.encrypt(mtrx_enc)

        #Strip the encoded to hide in matrix
        encoded_h = int(len(encoded)/44)
        if (len(encoded)/44)%encoded_h != 0:
            encoded_h += 1
        start = len(mtrx)
        end = len(mtrx)+encoded_h
        cnt = 0
        mtrx_add = {}
        enc_str = str
        for c in range(start,end):
            tmp = encoded[cnt:cnt+44]
            cnt +=44
            mtrx_add[c] = tmp.decode()
        for k,v in mtrx_add.items():
            mtrx[k] = v

        out = {'key':self._k,
               'fingerprint':fp,
               'salt': self.salt,
               'mtrx': mtrx,
               }
        return out





@dataclass(init=False)
class KyUser:
    _token:str
    _phase:dict
    _scnd:str

    def __init__(self, inp:KyMakerBase):
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

