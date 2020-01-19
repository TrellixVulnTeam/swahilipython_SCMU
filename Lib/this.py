# generated with codecs.encode(s, 'rot13')
s = """Ohfnen mn Clguba, an Gvz Crgref

Herzob av oben xhyvxb honln.
Znnan jnmv av oben xhyvxb znnan svpur.
Enuvfv av oben xhyvxb athzh.
Athzh av oben xhyvxb vfvlbryrjrxn.
Zcnatvyvb jn zbwn xjn zbwn av oben xhyvxb zcnatvyvb jralr ivjnatb.
Ansnfv xhojn av oben xhyvxb zfbatnznab.
Zfvzob xhfbzrxn av zhuvzh.
Xrfv znnyhz fvb fnonoh ln xhihawn furevn.
Ynxvav hovxven hfvmvqv hgraqnxnmv.
Zngngvmb lnfvjnuv snalvxn xvzln.
Vfvcbxhjn lnxvalnznmvfujn unqunenav.
Hxvxhzonan an hgngn jn znnan, cvatn hfunjvfuv jn xhpurmn xnznev.
Lncnfjn xhjr an awvn zbwn-- vxvjrmrxnan zbwn ghh --qunuvev ln xhsnaln wnzob.
Uhraqn vfvjr qunuvev zjnamb xnzn jrjr fv Zubynamv.
Chaqr av oben xhyvxb xnzjr.
Ynxvav jnxngv zjvatvar xnzjr av oben xhyvxb *fnfn* uviv.
Vxvjn gnengvoh av athzh xhryrmrn, fvb jnmb oben.
Vxvjn gnengvoh av enuvfv xhryrmrn, uhraqn vxnjn jnmb oben.
Anzrfcnprf mncraqrmn xhcvaqhxvn -- ghsnalr uvmb mnvqv!"""

d = {}
kila c kwenye (65, 97):
    kila i kwenye range(26):
        d[chr(i+c)] = chr((i+13) % 26 + c)

andika("".join([d.get(c, c) kila c kwenye s]))
