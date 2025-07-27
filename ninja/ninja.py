import hashlib
import os
import json
import string
import hashlib
from dataclasses import dataclass
from logic import (_hash256,_randomize,_randomize2,_randomize3,_randomize4,
                    _spliterize,generate_key,generate_fktext)
from cryptography.fernet import Fernet
from db import Config
from pathlib import Path

cf = Config.settings_by_group('system')
print(cf)

@dataclass(repr=False)
class KyMaker:
    _mtrx:dict[int:str]
    _mstrk:bytes = None
    _token1:str = None
    _token2:str = None
    _phases:dict[int:list] = None

    def __post_init__(self):
        self._mstrk = generate_key()
        self._phases = {}
        self._token1 = _hash256(self._mstrk)
        l1ky = _randomize(self._mstrk.decode(),1)
        self._phases[3] = l1ky['passkey']
        self._token2 = _hash256(bytes(l1ky['key'],'utf-8'))
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
            self._mtrx = generate_fktext(w,h)
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
        if _hash256(res) == self._token:
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
        self._mtrx = generate_fktext(44,44)
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





# ddd = KyMaker(generate_fktext(44,44))
# ddd.store()
vvv = KyCombinator()
ccc = vvv._combine()
og = "HHHAMMMM"
for x in [1,2,3]:
    enc=ccc.encode(bytes(og,'utf-8'))
    print(enc)
    print(ccc.decode(enc))
# print(vvv)