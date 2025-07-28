from ninja_hidden.core.crypt import KyCombinator,_randomize2_n,_urandomize2_n


# ddd = KyMaker(generate_fktext(44,44))
# ddd.store()
og=b'4XOftc3lyGMwcWFkRnxP-5pPBokFDVUYC0wR8oiKOug='
roken = "8wcRig5OxKD-OXfR3PoyF=4kpMunYWFCkVGBloc0PtwU"

passfrd = {1: [0, 2, 5, 5, 14, 13, 20, 2, 17, 3, 3, 3, 41, 23, 33, 9, 41, 14, 30, 6, 38, 40, 10, 13, 24, 17, 36, 24, 43, 4, 27, 6, 29, 42, 36, 12, 42, 16, 20, 14, 2, 5, 11, 10],
           2: [21, 11, 42, 10, 21, 3, 33, 25, 11, 39, 10, 43, 22, 7, 4, 16, 3, 0, 20, 37, 20, 37, 34, 41, 25, 40, 37, 28, 14, 42, 25, 7, 20, 0, 38, 19, 1, 11, 21, 28, 26, 35, 19, 14],
           3: [36, 11, 5, 16, 38, 42, 21, 2, 18, 39, 28, 20, 40, 1, 3, 35, 6, 19, 25, 8, 14, 43, 0, 15, 22, 10, 41, 17,31, 13, 27, 32, 26, 29, 9, 24, 7, 37, 12, 33, 23, 4, 34, 30],
           }
passfr = passfrd[1]
res = _randomize2_n(roken,passfr)
# print(res)
_urandomize2_n(res['fingerprint'])