import string
from pathlib import Path
from .objs import KeyGenerators, UserRegError
from dataclasses import dataclass
from cryptography.fernet import Fernet
from .crypt_funcs import *


@dataclass(repr=False)
class KyKeeper:
    pass


@dataclass(repr=False)
class KyMakerBase:
    user:str
    pwd:str
    salt:str = None
    _saltuser = None
    _k:bytes = None
    _result:dict = None
    _is_printed:bool = False

    def __repr__(self):
        return "Nothing to show."

    def __post_init__(self):
        if self.user is not None:
            if isinstance(self.user,bytes) or len(self.user) < 1:
                return UserRegError.Byte
            else:
                if '@' in self.user:
                    if not len(self.user.split('@')[1].split('.')) > 1:
                        return UserRegError.TLD
                else:
                    return UserRegError.NOMAIL
        else:
            return UserRegError.NOUSER

        if self.pwd is not None:
            if len(self.pwd) > 7 < 17:
                check = [False,False,False,False]
                err = ['Upper','lower','numbers','punctuation']
                for x in self.pwd:
                    if x.isupper():
                        check[0]=True
                    if x.islower():
                        check[1] = True
                    if x.isdigit():
                        check[2] = True
                    if x in string.punctuation:
                        check[3] = True
                res = [err[i] for i,x in enumerate(check) if not x ]
                if all(check):
                    print("Password ok.")
                else:
                   return UserRegError.PWDCONT
            else:
                return UserRegError.PWDLEN
        else:
            return UserRegError.NOPWD
        self._result = {}

        if self.salt is None:
            self.salt = KeyGenerators.text('all', 16)

        if self._saltuser is None:
            self._saltuser = KeyGenerators.text('all',16)


        if self._k is None:
            user,rest = self.user.split('@')
            tld = rest.split('.')[1]

            token_skel = f"{user}@{self.salt}@{self.pwd}@{tld}"
            ky = KeyGenerators.key_from_string(token_skel,bytes(self.salt,'utf-8'))
            self._k = ky

    def generate(self):
        pass


@dataclass(repr=False)
class KyMakerSystem(KyMakerBase):

    def show(self):
        atx = (f"KEY     :: {self._k.decode()}\n"
              f"SALT    :: {self.salt}\n"
              f"Finger  :: {self._fp['fingerprint']}\n"
              f"MATRIX  ::\n"
              f"{'\n'.join([v for k,v in self._mtrx.items()])[:-1]}")
        ttx = "Informations have already been provided."
        tx=atx
        if self._is_printed:
            tx = ttx
        self._is_printed = True
        return tx

    def generate(self)->dict:
        #First iteration
        randdm = randomize(self._k.decode(),1)
        print(randdm)
        fp = fingerize(randdm['key'], randdm['passkey'])
        self._fp = fp

        #Second iteration
        mtrx = KeyGenerators.matrix(44,44)
        mtrx_sig = randomize2(mtrx,self._k.decode())
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

        msb_fp = fingerprinting(prep[0])
        msb = "".join(msb_fp)
        lsb_fp = fingerprinting(prep[1])
        lsb = "".join(lsb_fp)
        sfx= " "
        mtrx_enc = f"{msb}{sfx}{lsb}"
        mtrx_enc = bytes(mtrx_enc,'utf-8')

        #Encode the mtrx res
        f_ky = Fernet(self._k)
        encoded = f_ky.encrypt(mtrx_enc)

        #Strip the encoded to hide in matrix
        line_len = len(self._mtrx[0])
        print("LINEN",line_len,len(self._mtrx))
        encoded_h = int(len(encoded)/line_len)
        if (len(encoded)/line_len)%encoded_h != 0:
            encoded_h += 1
        start = len(mtrx)
        end = len(mtrx)+encoded_h
        cnt = 0
        mtrx_add = {}
        enc_str = str
        for c in range(start,end):
            tmp = encoded[cnt:cnt+line_len]
            cnt +=line_len
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
class KyUserBase:
    _token:str
    _phase:dict
    _scnd:str

    def __init__(self, inp:KyMakerBase):
        self._token = inp._token1
        self._phase = inp._phases
        self._scnd = inp._scnd
        # print(inp._mstrk)

    def _check_key(self)->bytes:
        res = randomize3(self._phase,self._scnd)
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

