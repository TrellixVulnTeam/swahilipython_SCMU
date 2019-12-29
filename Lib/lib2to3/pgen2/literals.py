# Copyright 2004-2005 Elemental Security, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Safely evaluate Python string literals without using eval()."""

agiza re

simple_escapes = {"a": "\a",
                  "b": "\b",
                  "f": "\f",
                  "n": "\n",
                  "r": "\r",
                  "t": "\t",
                  "v": "\v",
                  "'": "'",
                  '"': '"',
                  "\\": "\\"}

eleza escape(m):
    all, tail = m.group(0, 1)
    assert all.startswith("\\")
    esc = simple_escapes.get(tail)
    ikiwa esc ni sio Tupu:
        rudisha esc
    ikiwa tail.startswith("x"):
        hexes = tail[1:]
        ikiwa len(hexes) < 2:
            ashiria ValueError("invalid hex string escape ('\\%s')" % tail)
        jaribu:
            i = int(hexes, 16)
        tatizo ValueError:
            ashiria ValueError("invalid hex string escape ('\\%s')" % tail) kutoka Tupu
    isipokua:
        jaribu:
            i = int(tail, 8)
        tatizo ValueError:
            ashiria ValueError("invalid octal string escape ('\\%s')" % tail) kutoka Tupu
    rudisha chr(i)

eleza evalString(s):
    assert s.startswith("'") ama s.startswith('"'), repr(s[:1])
    q = s[0]
    ikiwa s[:3] == q*3:
        q = q*3
    assert s.endswith(q), repr(s[-len(q):])
    assert len(s) >= 2*len(q)
    s = s[len(q):-len(q)]
    rudisha re.sub(r"\\(\'|\"|\\|[abfnrtv]|x.{0,2}|[0-7]{1,3})", escape, s)

eleza test():
    kila i kwenye range(256):
        c = chr(i)
        s = repr(c)
        e = evalString(s)
        ikiwa e != c:
            andika(i, c, s, e)


ikiwa __name__ == "__main__":
    test()
