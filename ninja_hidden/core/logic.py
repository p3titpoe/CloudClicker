import random
import string
import base64
import hashlib
from sys import call_tracing

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from db import Config

cf = Config.settings_by_group('system')
print(cf)

def _key_generator(passw:str|bytes,salt:bytes)->bytes:
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

lib={
'lower': list(string.ascii_lowercase),
'upper':list(string.ascii_uppercase),
'digit': list(string.digits),
'punct': list(string.punctuation)
}

def _libaccess(mode:str)->list[list]:
    combos = ['alpha','alphanum','all','alphapunct','numpunct']
    modes = [x for x in lib.keys()]
    trans = {'alpha': ['lower','upper'],
             'alphanum': ['lower','upper','digit'],
             'alphapunct': ['lower','upper','punct'],
             'all':modes,
             }

    mm = []
    ctrl = modes[::]
    ctrl.extend(combos)
    if mode in ctrl:
        if mode in combos:
            mm = [lib[k] for k in trans[mode]]
        else:
            mm = [lib[mode]]

    return mm

def generate_char_by_indx(mode: str, idx: int) ->str:
    res = _libaccess(mode)
    chosen_list:list = random.choice(res)
    return chosen_list[idx]

def generate_chars(mode:str, width: int = 80) ->str:
    mm =_libaccess(mode)
    # print(mm)
    out = ""
    if width == 1:
        chosen_list = random.choice(mm)
        char = random.choice(chosen_list)
        out = char

    else:
        while len(out) < width+1:
            chosen_list = random.choice(mm)
            char = random.choice(chosen_list)
            out += char
    return out


def generate_fktext(witdh:int,height:int):
    mtrx = {}
    for o in range(0,height):
        mtrx[o] = generate_chars('all', witdh)
    return mtrx

def generate_key():
    key = Fernet.generate_key()
    # key = b'q5WzHVJE0Gzpdlj_MwjFBS2yTcpGhyePglvfz02548U='
    # key =
    return key
