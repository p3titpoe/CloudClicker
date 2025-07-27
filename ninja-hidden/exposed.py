from core.logic import _hash256

def login(user:str,passwd:str)->str:
    res = {'user':'petrit','pwd':'04981b2bd3106a0fcaa91649f24040c2086c0f3e3b58678e9b639b8dfaf24cdf'}
    if user == res['user']:
        pwa = bytes(f"{user}@{passwd}@{salt.decode()}",'utf-8')
        pw =  _hash256(pwa)
        if pw == res['pwd']:
            return pwa
        else:
            print('Wrong Password')
