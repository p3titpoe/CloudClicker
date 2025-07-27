import random
import string
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from db import Config

cf = Config.settings_by_group('system')
print(cf)

def _key_generator(passw:str|bytes)->bytes:
    password = passw
    if isinstance(passw,str):
        password = bytes(passw,'utf-8')

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def _hash256(value:bytes)->str:
    res = hashlib.sha256(value)
    return res.hexdigest()

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

def _randomize(split:str,force_nmbr:int = None)->dict:
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

def _generate_txt_line(width:int = 80)->str:
    lower = list(string.ascii_lowercase)
    upper = list(string.ascii_uppercase)
    digit = list(string.digits)
    punct = list(string.punctuation)

    out = ""
    while len(out) < width+1:
        mm = (lower,upper,digit,punct)
        chosen_list = random.choice(mm)
        char = random.choice(chosen_list)
        out += char
    return out

def _randomize2(mtrx:dict, token:str, control:list=None)->dict:
    grid_x = [x for x in range(0,len(mtrx[0]))]
    grid_y = [x for x in mtrx.keys()]
    ctrl = None if control is None else [x[1] for x in control]
    pk1 = []
    pk2 = []
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

def generate_fktext(witdh:int,height:int):
    mtrx = {}
    for o in range(0,height):
        mtrx[o] = _generate_txt_line(witdh)
    return mtrx

def generate_key():
    key = Fernet.generate_key()
    # key = b'q5WzHVJE0Gzpdlj_MwjFBS2yTcpGhyePglvfz02548U='
    # key =
    return key
